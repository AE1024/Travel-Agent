from datetime import date
from typing import Optional
from typing_extensions import TypedDict, Annotated
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from agent.tools.flights import search_flights
from agent.tools.hotels import search_hotels
from agent.tools.transport import search_transport

from dotenv import load_dotenv

load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    raise EnvironmentError("CEREBRAS_API_KEY bulunamadı. backend/.env dosyasını kontrol edin.")
# ── State ─────────────────────────────────────────────────────────────────────
# phase akışı:  "flight" → "hotel" → "transport" → "done"
# Her onay kapısı (approval node) phase'i bir sonraki değere atar.
# Orchestrator, phase değerine bakarak ne yapacağını bilir.

class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    phase: str                        # "flight" | "hotel" | "transport" | "done"
    selected_flight: Optional[str]
    selected_hotel: Optional[str]
    selected_transport: Optional[str]

# ── Tools ──────────────────────────────────────────────────────────────────────

all_tools = [search_flights, search_hotels, search_transport]
tool_node = ToolNode(all_tools)

# ── LLM ───────────────────────────────────────────────────────────────────────
base_llm = ChatOpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=CEREBRAS_API_KEY,
    model="qwen-3-235b-a22b-instruct-2507",
    temperature=0.3,
    max_tokens=2048
)
llm = base_llm.bind_tools(all_tools)

SYSTEM_PROMPT = f"""Sen profesyonel ve çözüm odaklı bir Seyahat Planlama Asistanısın.
Bugünün tarihi: {date.today()}.

### GENEL KURALLAR:
1. Eksik veri varsa nazikçe sor, varsayımda bulunma.
2. Şehir isimlerini her zaman AIRPORT IATA koduna çevir — city code değil, airport code kullan.
3. Tarihleri YYYY-MM-DD formatında kullan.
4. Ham API verisi sunma; sonuçları listelemiş, okunabilir biçimde özetle.
5. Sadece uçuş, otel ve seyahat konularına odaklan.

### KRİTİK IATA KURALI — AIRPORT KODU KULLAN, ŞEHİR KODU KULLANMA:
Aşağıdaki örnekleri KESINLIKLE uygula:
- İstanbul → IST (SAW değil, IST kullan; Sabiha Gökçen istenmedikçe)
- Londra / London → LHR  (LON değil — LON city code, LHR airport code)
- Paris → CDG  (PAR değil)
- New York → JFK  (NYC değil)
- Milano / Milan → MXP  (MIL değil)
- Roma / Rome → FCO  (ROM değil)
- Tokyo → NRT  (TYO değil)
- Dubai → DXB  (DBX değil)
- Amsterdam → AMS
- Berlin → BER
- Barselona / Barcelona → BCN
- Madrid → MAD
- Viyana / Vienna → VIE
- Münih / Munich → MUC
- Frankfurt → FRA
- Brüksel / Brussels → BRU
- Atina / Athens → ATH
- Moskova / Moscow → SVO
- Kahire / Cairo → CAI
Genel kural: Google Flights'ın kabul ettiği 3 harfli HAVALIMANÜ IATA kodunu kullan.
City code (LON, PAR, NYC vb.) ASLA kullanma.

### UÇUŞ AKIŞI (phase = "flight"):
- Zorunlu: kalkış · varış · tarih.
- Geçmiş tarihler için arama yapma.
- Uçuşları listeledikten sonra DUR — kullanıcı seçim yapacak.

### OTEL AKIŞI (phase = "hotel"):
- Zorunlu: varış şehri · check_in_date · check_out_date · airport_iata.
- Uçuştan gelen tarih ve IATA kodunu kullan.
- Otelleri listeledikten sonra DUR — kullanıcı seçim yapacak.

### TRANSFER AKIŞI (phase = "transport"):
- Seçilen uçuşun varış havalimanı ve seçilen otelin adını kullan.
- Transfer seçeneklerini listeledikten sonra DUR — kullanıcı seçim yapacak.
"""

_PHASE_HINT = {
    "flight":    "\n\n**MEVCUT AŞAMA → UÇUŞ.** search_flights aracını çağır ve seçenekleri listele.",
    "hotel": """\n\n**MEVCUT AŞAMA → OTEL.**

Uçuştan otomatik gelen bilgiler — bunları tekrar SORMA, konuşma geçmişinden al:
  • destination_city ve airport_iata → seçilen uçuşun varış şehri/havalimanı
  • check_in_date → seçilen uçuşun kalkış/varış tarihi

ZORUNLU — yalnızca bu eksikse sor:
  • check_out_date: kaç gece kalacaklar?

OPSİYONEL — kullanıcı belirtirse parametreye ekle, belirtmezse sorma:
  • min_stars (yıldız sayısı)
  • max_budget (kişi başı TRY bütçe)
  • amenities: wifi / spa / havuz / gym / kahvaltı / otopark
  • near_airport=True: kullanıcı "havalimanına yakın", "airport yakını", "transfer kolay" gibi ifadeler kullandıysa geç — seçilen uçuşun airport_iata'sını da mutlaka ver

  • sort_by: kullanıcı "fiyata göre", "ucuzdan pahalıya", "en ucuz" derse → "price"; "puana göre", "en iyi" derse → "rating"

NOT: Arama sonuçları otomatik olarak Booking.com, Hotels.com ve Trivago platformlarını kapsar.

KURAL — şu adımları SIRASYLA uygula:
  1. Eğer check_out_date bilgisi konuşmada yoksa, aşağıdaki soruyu TAM OLARAK bir kez sor:
     "Kaç gece kalacaksınız? İsterseniz tercihlerinizi de belirtebilirsiniz: yıldız, bütçe, wifi/spa/havuz gibi özellikler."
  2. Kullanıcı gece sayısını söylediği anda HEMEN search_hotels çağır — tekrar sorma.
  3. Opsiyonel bilgiler verilmediyse o parametreleri None bırak, varsayım yapma.""",

    "transport": """\n\n**MEVCUT AŞAMA → TRANSFER.**

Konuşma geçmişinden otomatik al — TEKRAR SORMA:
  • airport_iata → seçilen uçuşun varış havalimanı IATA kodu
  • hotel_name   → seçilen otelin adı

OPSİYONEL — kullanıcı belirtirse ekle, belirtmezse bırak:
  • via: driving / transit / walking / cycling / flight / best

KURAL: Bilgileri konuşma geçmişinden aldıktan sonra HEMEN search_transport çağır, kullanıcıya sormadan.""",
    "done":      "\n\n**TÜM SEÇİMLER TAMAMLANDI.**",
}


def orchestrator(state: GraphState) -> dict:
    phase = state.get("phase", "flight")
    if phase == "done":
        return {"messages": []}
    system = SystemMessage(content=SYSTEM_PROMPT + _PHASE_HINT.get(phase, ""))
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


_APPROVAL_PROMPTS = {
    "flight":    "✈ Lütfen bir uçuş seçin (örn: '1') ya da 'yeniden ara' yazın:",
    "hotel":     "🏨 Lütfen bir otel seçin (örn: '2') ya da 'yeniden ara' yazın:",
    "transport": "🚗 Transfer seçeneğini seçin (örn: '1') ya da 'atla' / 'yeniden ara' yazın:",
}

_NEXT_PHASE = {"flight": "hotel", "hotel": "transport", "transport": "done"}

_SELECTION_KEY = {"flight": "selected_flight", "hotel": "selected_hotel", "transport": "selected_transport"}


def approval(state: GraphState) -> dict:
    """Tek onay kapısı — phase'e göre doğru soruyu sorar ve state'i günceller."""
    phase = state.get("phase", "flight")
    selection = interrupt(_APPROVAL_PROMPTS[phase])

    is_retry = any(k in selection.lower() for k in ("yeniden", "retry", "tekrar", "başka"))
    is_skip  = phase == "transport" and "atla" in selection.lower()

    if is_retry:
        return {
            "messages": [HumanMessage(content=f"Kullanıcı: {selection}")],
            "phase": phase,   # aynı phase kalır → orchestrator tekrar arar
        }

    value = "Atlandı" if is_skip else selection

    # Sonraki phase için orchestrator'a açık bir yönerge mesajı ekle
    _transition_msg = {
        "flight": f"Uçuş seçildi: {value}. Şimdi otel tercihlerini kullanıcıya sor (kaç gece, yıldız, özellikler). Sormadan arama yapma.",
        "hotel":  f"Otel seçildi: {value}. Transfer aşamasına geç. airport_iata ve hotel_name bilgilerini konuşma geçmişinden al ve search_transport çağır.",
        "transport": f"Transfer seçildi: {value}. Seyahat özeti hazırla.",
    }

    return {
        "messages": [HumanMessage(content=_transition_msg.get(phase, f"Seçim: {value}"))],
        _SELECTION_KEY[phase]: value,
        "phase": _NEXT_PHASE[phase],
    }


def summary_node(state: GraphState) -> dict:
    """Seyahat özetini oluşturur."""
    prompt = HumanMessage(content=(
        "Seyahat planı tamamlandı! Aşağıdaki seçimleri güzel ve profesyonel bir özet olarak sun. "
        "Rezervasyon linklerini de ekle:\n"
        f"• Uçuş: {state.get('selected_flight', 'Seçilmedi')}\n"
        f"• Otel: {state.get('selected_hotel', 'Seçilmedi')}\n"
        f"• Transfer: {state.get('selected_transport', 'Seçilmedi')}\n"
        "Toplam tahmini maliyeti de hesapla."
    ))
    response = base_llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"] + [prompt]
    )
    return {"messages": [response]}


# ── Routing ────────────────────────────────────────────────────────────────────

def route_after_orchestrator(state: GraphState) -> str:
    """
    Karar ağacı:
      1. LLM tool çağırdıysa           → tools
      2. phase == "done"               → summary
      3. Önceki mesaj ToolMessage ise  → approval  (LLM sonuçları sundu, kullanıcı seçecek)
      4. Aksi hâlde                    → END       (LLM bilgi topluyor, kullanıcı cevap bekliyor)
    """
    messages = state["messages"]
    last = messages[-1]

    if getattr(last, "tool_calls", None):
        return "tools"

    if state.get("phase") == "done":
        return "summary"

    if len(messages) >= 2 and isinstance(messages[-2], ToolMessage):
        return "approval"

    return END

# ── Graph ──────────────────────────────────────────────────────────────────────
graph = StateGraph(GraphState)

graph.add_node("orchestrator", orchestrator)
graph.add_node("tools",        tool_node)
graph.add_node("approval",     approval)
graph.add_node("summary",      summary_node)

graph.add_edge(START, "orchestrator")

graph.add_conditional_edges(
    "orchestrator",
    route_after_orchestrator,
    {"tools": "tools", "approval": "approval", "summary": "summary", END: END},
)

graph.add_edge("tools",    "orchestrator")
graph.add_edge("approval", "orchestrator")
graph.add_edge("summary",  END)

app = graph.compile(checkpointer=MemorySaver())

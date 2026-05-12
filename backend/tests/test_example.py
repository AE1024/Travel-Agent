import os
import pytest
from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.metrics import GEval
from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_openai import ChatOpenAI

load_dotenv()

class CerebrasJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.client = ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0,
        )

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        return self.client.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        res = await self.client.ainvoke(prompt)
        return res.content

    def get_model_name(self) -> str:
        return "llama-3.3-70b-versatile"


judge = CerebrasJudge()


# ── Metrikler ──────────────────────────────────────────────────────────────────

iata_metric = GEval(
    name="IATA Doğruluğu",
    criteria=(
        "Agent cevabında şehir isimleri doğru IATA airport koduna çevrilmiş mi? "
        "İstanbul→IST, Paris→CDG, Londra→LHR, New York→JFK, Dubai→DXB olmalı. "
        "City code (LON, PAR, NYC vb.) kullanılmışsa başarısız say."
    ),
    evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
    threshold=0.7,
    model=judge,
)

phase_metric = GEval(
    name="Faz Geçiş Kalitesi",
    criteria=(
        "Agent seçim yapıldıktan sonra doğru bir sonraki aşamaya geçti mi? "
        "Uçuş seçimi → otel sorusu, otel seçimi → transfer araması bekleniyor. "
        "Yanlış soru sorulduysa veya yanlış araç çağrıldıysa başarısız say."
    ),
    evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
    threshold=0.7,
    model=judge,
)

correctness_metric = GEval(
    name="Cevap Doğruluğu",
    criteria=(
        "Agent'ın cevabı kullanıcının seyahat sorusuna doğru ve eksiksiz yanıt veriyor mu? "
        "Eksik bilgi istenmişse nazikçe sorulmuş olmalı. "
        "Gereksiz varsayım yapılmışsa başarısız say."
    ),
    evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
    threshold=0.5,
    model=judge,
)


# ── Test 1: IATA Kodu Doğruluğu ───────────────────────────────────────────────

def test_iata_istanbul_paris():
    test_case = LLMTestCase(
        input="İstanbul'dan Paris'e 15 Temmuz 2026 için uçuş ara",
        actual_output=(
            "IST → CDG uçuşlarını arıyorum.\n"
            "1. Turkish Airlines TK1827 | 08:00 → 10:30 | 3s 30dk | 4.500 TRY\n"
            "2. Pegasus PC5502 | 14:00 → 16:30 | 3s 30dk | 3.800 TRY\n"
            "✈ Lütfen bir uçuş seçin (örn: '1') ya da 'yeniden ara' yazın:"
        ),
        expected_output=(
            "IST ve CDG kodları kullanılmalı. "
            "Uçuş listesi sunulmalı ve kullanıcıdan seçim istenmeli."
        ),
    )
    assert_test(test_case, [iata_metric])


def test_iata_london_newyork():
    test_case = LLMTestCase(
        input="Londra'dan New York'a uçuş bul",
        actual_output=(
            "LHR → JFK rotasını arıyorum.\n"
            "1. British Airways BA117 | 11:00 → 13:45 | 7s 45dk | $650\n"
            "2. Virgin Atlantic VS003 | 14:30 → 17:15 | 7s 45dk | $580\n"
            "✈ Lütfen bir uçuş seçin:"
        ),
        expected_output=(
            "LHR ve JFK kodları kullanılmalı (LON veya NYC değil). "
            "Uçuş listesi sunulmalı."
        ),
    )
    assert_test(test_case, [iata_metric])


# ── Test 2: Faz Geçişleri ─────────────────────────────────────────────────────

def test_flight_to_hotel_transition():
    test_case = LLMTestCase(
        input="1 numaralı uçuşu seçiyorum",
        actual_output=(
            "Uçuşunuz seçildi! ✅\n"
            "Otel aşamasına geçiyoruz.\n"
            "Kaç gece kalacaksınız? "
            "İsterseniz tercihlerinizi de belirtebilirsiniz: yıldız, bütçe, wifi/spa/havuz gibi özellikler."
        ),
        expected_output=(
            "Uçuş seçimi onaylanmalı ve otel için kaç gece sorusu sorulmalı. "
            "check_in tarihi otomatik alınmalı, tekrar sorulmamalı."
        ),
    )
    assert_test(test_case, [phase_metric])


def test_hotel_to_transport_transition():
    test_case = LLMTestCase(
        input="2 numaralı oteli seçiyorum",
        actual_output=(
            "Oteliniz seçildi! ✅\n"
            "Transfer aşamasına geçiyoruz.\n"
            "CDG havalimanından otelinize transfer seçenekleri:\n"
            "1. Taksi ~45 dk | €60\n"
            "2. RER B treni ~35 dk | €11\n"
            "3. Özel transfer ~40 dk | €85\n"
            "🚗 Transfer seçeneğini seçin:"
        ),
        expected_output=(
            "Otel seçimi onaylanmalı ve transfer seçenekleri listelenmeli. "
            "Havalimanı kodu seçilen uçuştan alınmalı."
        ),
    )
    assert_test(test_case, [phase_metric])


# ── Test 3: Eksik Bilgi Yönetimi ──────────────────────────────────────────────

def test_missing_destination():
    test_case = LLMTestCase(
        input="Uçuş aramak istiyorum",
        actual_output=(
            "Tabii ki yardımcı olabilirim! 😊\n"
            "Nereden nereye uçmak istiyorsunuz? "
            "Kalkış şehri, varış şehri ve tarih bilgisini paylaşır mısınız?"
        ),
        expected_output=(
            "Eksik bilgi (kalkış, varış, tarih) nazikçe sorulmalı. "
            "Varsayımda bulunulmamalı."
        ),
    )
    assert_test(test_case, [correctness_metric])


def test_past_date_rejection():
    test_case = LLMTestCase(
        input="İstanbul'dan Antalya'ya 1 Ocak 2020 için uçuş ara",
        actual_output=(
            "Üzgünüm, geçmiş tarihlere uçuş araması yapamam. "
            "Bugün veya sonrasına ait bir tarih belirtir misiniz?"
        ),
        expected_output=(
            "Geçmiş tarih için arama yapılmamalı ve kullanıcı bilgilendirilmeli."
        ),
    )
    assert_test(test_case, [correctness_metric])


def test_off_topic_rejection():
    test_case = LLMTestCase(
        input="Bana makarna tarifi ver",
        actual_output=(
            "Ben bir seyahat planlama asistanıyım. "
            "Size yalnızca uçuş, otel ve transfer konularında yardımcı olabilirim. "
            "Bir seyahat planlamak ister misiniz?"
        ),
        expected_output=(
            "Seyahat dışı konularda yardım reddedilmeli ve "
            "kullanıcı seyahat konularına yönlendirilmeli."
        ),
    )
    assert_test(test_case, [correctness_metric])

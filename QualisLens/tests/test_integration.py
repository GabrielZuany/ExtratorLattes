"""
Testes de integração: pipeline completo sem LLM.

Executa os casos de teste dos fixtures easy/mid/hard (raiz e subpastas 01-10)
e verifica que o algoritmo de fuzzy matching + busca exata resolve
corretamente sem LLM.

Organização dos fixtures:
  test/easy/entrada.csv          ← fixture original (5 casos)
  test/easy/01/entrada.csv       ← caso de teste 01 (5 casos)
  ...
  test/easy/10/entrada.csv       ← caso de teste 10 (5 casos)
  (idem para mid/ e hard/)
"""

import csv
from pathlib import Path

import pytest
from matcher import match
from constants import STATUS_AUTO_FUZZY, STATUS_EXATO, STATUS_LLM_MISS, THRESHOLD_AUTO

TEST_DIR = Path(__file__).parent.parent / "test"

# Subpastas numeradas disponíveis
_SUBFOLDERS = [f"{i:02d}" for i in range(1, 11)]


def _ler_fixture(nivel: str, sub: str = "") -> list[dict]:
    """Lê o CSV de entrada de um fixture (raiz ou subpasta numerada)."""
    if sub:
        path = TEST_DIR / nivel / sub / "entrada.csv"
    else:
        path = TEST_DIR / nivel / "entrada.csv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _ler_expected(nivel: str, sub: str = "") -> list[dict]:
    """Lê o CSV de saída esperada de um fixture."""
    if sub:
        path = TEST_DIR / nivel / sub / "entrada_output.csv"
    else:
        path = TEST_DIR / nivel / "entrada_output.csv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _run_row(row: dict, db) -> dict:
    """Executa match() para uma linha do CSV de entrada."""
    sigla = row.get("sigla_conferencia", "").strip() or None
    return match(
        nome_conferencia=row["nome_conferencia"],
        ano=int(row["ano_publicacao"]),
        sigla_conferencia=sigla,
        db=db,
    )


# ── EASY ──────────────────────────────────────────────────────────────────────

class TestFixtureEasy:
    """
    Casos fáceis: todos têm sigla explícita e nome exato na base.
    Resultado esperado: STATUS_EXATO em todos, com estrato correto.
    """

    @pytest.fixture(autouse=True)
    def _load(self, db):
        self.db = db
        self.rows = _ler_fixture("easy")
        self.expected = _ler_expected("easy")

    def _run(self, i: int) -> dict:
        row = self.rows[i]
        return match(
            nome_conferencia=row["nome_conferencia"],
            ano=int(row["ano_publicacao"]),
            sigla_conferencia=row.get("sigla_conferencia") or None,
            db=self.db,
        )

    def test_sbrc_exato(self):
        result = self._run(0)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == self.expected[0]["qualis_estrato"]

    def test_icse_exato(self):
        result = self._run(1)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A1"

    def test_aaai_exato(self):
        result = self._run(2)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A1"

    def test_vldb_exato(self):
        # VLDB pode estar somente na base 2017-2020; o match deve ser EXATO (extrapolado)
        result = self._run(3)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A1"

    def test_stoc_exato(self):
        result = self._run(4)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A1"

    def test_todos_exato_score_100(self):
        for i in range(len(self.rows)):
            result = self._run(i)
            if result["qualis_status"] == STATUS_EXATO:
                assert result["qualis_score_fuzzy"] == 100.0


# ── MID ───────────────────────────────────────────────────────────────────────

class TestFixtureMid:
    """
    Casos intermediários: nomes parcialmente abreviados, alguns com sigla.
    Resultado esperado: mix de EXATO e AUTO_FUZZY, estrato correto.
    """

    @pytest.fixture(autouse=True)
    def _load(self, db):
        self.db = db
        self.rows = _ler_fixture("mid")
        self.expected = _ler_expected("mid")

    def _run(self, i: int) -> dict:
        row = self.rows[i]
        sigla = row.get("sigla_conferencia", "").strip() or None
        return match(
            nome_conferencia=row["nome_conferencia"],
            ano=int(row["ano_publicacao"]),
            sigla_conferencia=sigla,
            db=self.db,
        )

    def test_ccs_exato_por_sigla(self):
        # CCS com sigla explícita → EXATO
        result = self._run(0)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A1"

    def test_bracis_exato_por_sigla(self):
        result = self._run(1)
        assert result["qualis_status"] == STATUS_EXATO
        assert result["qualis_estrato"] == "A3"

    def test_ccgrid_auto_fuzzy_sem_sigla(self):
        # "Int'l Symp. on Cluster, Cloud and Grid Computing" sem sigla → AUTO_FUZZY
        result = self._run(2)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO

    def test_cbms_auto_fuzzy(self):
        # "IEEE Int'l Symp. on Computer-Based Medical Systems" sem sigla
        result = self._run(3)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO

    def test_dcc_exato_por_nome(self):
        # "Data Compression Conference" sem sigla → match por nome (pode ser EXATO ou AUTO_FUZZY)
        result = self._run(4)
        expected_estrato = self.expected[4]["qualis_estrato"]
        assert result["qualis_status"] in (STATUS_EXATO, STATUS_AUTO_FUZZY)
        assert result["qualis_estrato"] == expected_estrato

    def test_mid_sem_llm_necessario(self):
        # Nenhum caso mid deve precisar de LLM (todos resolvem por fuzzy ou exato)
        for i in range(len(self.rows)):
            result = self._run(i)
            assert not result.get("_precisa_llm", False), (
                f"Linha {i} ({self.rows[i]['nome_conferencia']!r}) requer LLM inesperadamente"
            )

    def test_estrato_nunca_nulo_para_exato_ou_auto_fuzzy(self):
        for i in range(len(self.rows)):
            result = self._run(i)
            if result["qualis_status"] in (STATUS_EXATO, STATUS_AUTO_FUZZY):
                assert result["qualis_estrato"] is not None, (
                    f"Linha {i}: status={result['qualis_status']} mas estrato=None"
                )


# ── HARD ──────────────────────────────────────────────────────────────────────

class TestFixtureHard:
    """
    Casos difíceis: nomes muito abreviados, sem sigla, multi-token truncado.
    O algoritmo deve resolver via AUTO_FUZZY (score >= 75) sem LLM.
    """

    @pytest.fixture(autouse=True)
    def _load(self, db):
        self.db = db
        self.rows = _ler_fixture("hard")
        self.expected = _ler_expected("hard")

    def _run(self, i: int) -> dict:
        row = self.rows[i]
        sigla = row.get("sigla_conferencia", "").strip() or None
        return match(
            nome_conferencia=row["nome_conferencia"],
            ano=int(row["ano_publicacao"]),
            sigla_conferencia=sigla,
            db=self.db,
        )

    def test_neurips_abreviado(self):
        # "C. on N Inf Proc. Sys." → deve ter score >= THRESHOLD_AUTO
        result = self._run(0)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO
        assert result["qualis_estrato"] == self.expected[0]["qualis_estrato"]

    def test_stoc_abreviado(self):
        # "Ann. ACM Symp. on Theory of Comp."
        result = self._run(1)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO
        assert result["qualis_estrato"] == self.expected[1]["qualis_estrato"]

    def test_iccad_abreviado(self):
        # "IEEE/ACM Int'l C. on Comp.-Aided Des."
        result = self._run(2)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO

    def test_workshop_abreviado(self):
        # "Wksp. on Emb. Syst. Sec. & Verif."
        result = self._run(3)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO

    def test_spice_abreviado(self):
        # "Int'l Conf. on SW Proc. Impr. & Cap. Det."
        result = self._run(4)
        assert result["qualis_status"] == STATUS_AUTO_FUZZY
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO

    def test_hard_todos_resolvem_sem_llm(self):
        """Verifica que todos os casos hard resolvem sem acionar o LLM."""
        for i, row in enumerate(self.rows):
            result = self._run(i)
            assert not result.get("_precisa_llm", False), (
                f"Linha {i} ({row['nome_conferencia']!r}) requer LLM — "
                f"score={result['qualis_score_fuzzy']:.1f}"
            )

    def test_hard_estrato_nunca_nulo_em_auto_fuzzy(self):
        for i in range(len(self.rows)):
            result = self._run(i)
            if result["qualis_status"] == STATUS_AUTO_FUZZY:
                assert result["qualis_estrato"] is not None, (
                    f"Linha {i}: AUTO_FUZZY mas estrato=None"
                )

    def test_candidatos_retornados_mesmo_em_hard(self):
        for i in range(len(self.rows)):
            result = self._run(i)
            assert result["_candidatos_lista"], (
                f"Linha {i}: lista de candidatos vazia para {self.rows[i]['nome_conferencia']!r}"
            )


# ── REGRESSÃO: estrato esperado por caso ────────────────────────────────────

CASOS_REGRESSAO = [
    # (nome, sigla, ano, estrato_esperado, descricao)
    ("SBRC - Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos", "SBRC", 2022, "A4", "SBRC 2022"),
    ("International Conference on Software Engineering", "ICSE", 2023, "A1", "ICSE 2023"),
    ("AAAI Conference on Artificial Intelligence", "AAAI", 2022, "A1", "AAAI 2022"),
    ("Annual Symposium on Theory of Computing", "STOC", 2021, "A1", "STOC 2021"),
    ("ACM Conf. on Computer and Communications Security", "CCS", 2023, "A1", "CCS 2023"),
    ("Brazilian Conf. on Intelligent Systems", "BRACIS", 2022, "A3", "BRACIS 2022"),
    ("C. on N Inf Proc. Sys.", None, 2023, "A1", "NeurIPS abreviado 2023"),
    ("Ann. ACM Symp. on Theory of Comp.", None, 2022, "A1", "STOC abreviado 2022"),
]


@pytest.mark.parametrize("nome,sigla,ano,estrato_esperado,desc", CASOS_REGRESSAO)
def test_regressao_estrato(db, nome, sigla, ano, estrato_esperado, desc):
    """Verifica que o estrato retornado corresponde ao valor esperado."""
    result = match(nome, ano, sigla, db)
    assert result["qualis_estrato"] == estrato_esperado, (
        f"[{desc}] Esperado={estrato_esperado!r}, "
        f"Obtido={result['qualis_estrato']!r}, "
        f"Status={result['qualis_status']}, "
        f"Score={result['qualis_score_fuzzy']}"
    )


# ── FIXTURES NUMERADOS (easy/01–10, mid/01–10, hard/01–10) ──────────────────
#
# Propriedades invariantes que valem para TODOS os suites numerados:
#   easy/XX  → todos os casos devem ser EXATO com score 100
#   mid/XX   → todos devem ser EXATO ou AUTO_FUZZY; nenhum precisa de LLM
#   hard/XX  → todos devem ser AUTO_FUZZY com score ≥ THRESHOLD_AUTO

_EASY_SUBS  = _SUBFOLDERS
_MID_SUBS   = _SUBFOLDERS
_HARD_SUBS  = _SUBFOLDERS


@pytest.mark.parametrize("sub", _EASY_SUBS)
def test_easy_suite_todos_exato(db, sub):
    """Todos os casos de easy/XX devem ser EXATO com score 100."""
    rows = _ler_fixture("easy", sub)
    for row in rows:
        result = _run_row(row, db)
        nome = row["nome_conferencia"]
        assert result["qualis_status"] == STATUS_EXATO, (
            f"easy/{sub} | {nome!r} → status={result['qualis_status']} "
            f"(esperado EXATO)"
        )
        assert result["qualis_score_fuzzy"] == 100.0, (
            f"easy/{sub} | {nome!r} → score={result['qualis_score_fuzzy']} "
            f"(esperado 100.0)"
        )


@pytest.mark.parametrize("sub", _EASY_SUBS)
def test_easy_suite_estrato_correto(db, sub):
    """O estrato de easy/XX deve coincidir com o CSV de saída esperada."""
    rows = _ler_fixture("easy", sub)
    expected = _ler_expected("easy", sub)
    for row, exp in zip(rows, expected):
        result = _run_row(row, db)
        assert result["qualis_estrato"] == exp["qualis_estrato"], (
            f"easy/{sub} | {row['nome_conferencia']!r} → "
            f"estrato={result['qualis_estrato']!r} (esperado {exp['qualis_estrato']!r})"
        )


@pytest.mark.parametrize("sub", _MID_SUBS)
def test_mid_suite_sem_llm(db, sub):
    """Nenhum caso de mid/XX deve precisar de LLM."""
    rows = _ler_fixture("mid", sub)
    for row in rows:
        result = _run_row(row, db)
        assert not result.get("_precisa_llm", False), (
            f"mid/{sub} | {row['nome_conferencia']!r} requer LLM inesperadamente "
            f"(score={result['qualis_score_fuzzy']:.1f})"
        )


@pytest.mark.parametrize("sub", _MID_SUBS)
def test_mid_suite_status_valido(db, sub):
    """Todos os casos de mid/XX devem ser EXATO ou AUTO_FUZZY."""
    rows = _ler_fixture("mid", sub)
    valid = {STATUS_EXATO, STATUS_AUTO_FUZZY}
    for row in rows:
        result = _run_row(row, db)
        assert result["qualis_status"] in valid, (
            f"mid/{sub} | {row['nome_conferencia']!r} → "
            f"status={result['qualis_status']!r} (esperado EXATO ou AUTO_FUZZY)"
        )


@pytest.mark.parametrize("sub", _MID_SUBS)
def test_mid_suite_estrato_correto(db, sub):
    """O estrato de mid/XX deve coincidir com o CSV de saída esperada."""
    rows = _ler_fixture("mid", sub)
    expected = _ler_expected("mid", sub)
    for row, exp in zip(rows, expected):
        result = _run_row(row, db)
        if result["qualis_status"] in (STATUS_EXATO, STATUS_AUTO_FUZZY):
            assert result["qualis_estrato"] == exp["qualis_estrato"], (
                f"mid/{sub} | {row['nome_conferencia']!r} → "
                f"estrato={result['qualis_estrato']!r} (esperado {exp['qualis_estrato']!r})"
            )


@pytest.mark.parametrize("sub", _HARD_SUBS)
def test_hard_suite_auto_fuzzy(db, sub):
    """Todos os casos de hard/XX devem ser AUTO_FUZZY com score ≥ THRESHOLD_AUTO."""
    rows = _ler_fixture("hard", sub)
    for row in rows:
        result = _run_row(row, db)
        nome = row["nome_conferencia"]
        assert result["qualis_status"] == STATUS_AUTO_FUZZY, (
            f"hard/{sub} | {nome!r} → status={result['qualis_status']!r} "
            f"(esperado AUTO_FUZZY)"
        )
        assert result["qualis_score_fuzzy"] >= THRESHOLD_AUTO, (
            f"hard/{sub} | {nome!r} → score={result['qualis_score_fuzzy']:.1f} "
            f"(esperado ≥ {THRESHOLD_AUTO})"
        )


@pytest.mark.parametrize("sub", _HARD_SUBS)
def test_hard_suite_sem_llm(db, sub):
    """Nenhum caso de hard/XX deve precisar de LLM."""
    rows = _ler_fixture("hard", sub)
    for row in rows:
        result = _run_row(row, db)
        assert not result.get("_precisa_llm", False), (
            f"hard/{sub} | {row['nome_conferencia']!r} requer LLM inesperadamente "
            f"(score={result['qualis_score_fuzzy']:.1f})"
        )


@pytest.mark.parametrize("sub", _HARD_SUBS)
def test_hard_suite_estrato_nao_nulo(db, sub):
    """Todos os AUTO_FUZZY de hard/XX devem ter estrato preenchido."""
    rows = _ler_fixture("hard", sub)
    for row in rows:
        result = _run_row(row, db)
        if result["qualis_status"] == STATUS_AUTO_FUZZY:
            assert result["qualis_estrato"] is not None, (
                f"hard/{sub} | {row['nome_conferencia']!r} → estrato=None"
            )

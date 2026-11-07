import numpy as np
import pytest

from src.eval.metrics import bootstrap_pareado, c1, c2, c3, cp_superior, ic95, tasas, umbral_fnr


def test_umbral_respeta_fnr_en_calibracion():
    rng = np.random.default_rng(0)
    y = np.array([1] * 300 + [0] * 700)
    s = np.concatenate([rng.uniform(0.3, 1, 300), rng.uniform(0, 0.7, 700)])
    tau = umbral_fnr(s, y, 0.01)
    t = tasas(s, y, tau)
    assert t["FN"] <= 3 and t["FNR"] <= 0.01
    # es el mayor posible: subir un poco el umbral rompe el límite
    pos = np.sort(s[y == 1])
    assert tasas(s, y, pos[4])["FN"] > 3


def test_tasas_basicas():
    s = np.array([0.9, 0.2, 0.8, 0.1])
    y = np.array([1, 1, 0, 0])
    t = tasas(s, y, 0.5)
    assert (t["FN"], t["TN"], t["FNR"], t["TNR"]) == (1, 1, 0.5, 0.5)


def test_cp_coincide_con_regla_del_tres():
    assert cp_superior(0, 299) == pytest.approx(0.01, abs=2e-4)
    assert cp_superior(5, 500) == pytest.approx(0.0209, abs=5e-4)


def test_veredictos_c2():
    assert c2(4, 600).veredicto == "pasa"
    assert c2(4, 450).veredicto == "no concluyente"   # menos de 500 positivos
    assert c2(8, 600).veredicto == "no pasa"          # 1,33 % > 1 %
    assert c2(0, 100).veredicto == "no concluyente"   # cota 2,95 % > 2,5 %


def test_veredictos_c1_c3():
    assert c1(0.40, np.full(100, 0.30)).veredicto == "pasa"
    assert c1(0.30, np.linspace(0.20, 0.40, 100)).veredicto == "no concluyente"
    assert c1(0.20, np.full(100, 0.20)).veredicto == "no pasa"
    assert c3(0.08, np.linspace(0.01, 0.15, 100)).veredicto == "pasa"
    assert c3(0.08, np.linspace(-0.02, 0.15, 100)).veredicto == "no concluyente"
    assert c3(0.03, np.linspace(0.01, 0.05, 100)).veredicto == "no pasa"


def test_bootstrap_por_grupo_es_pareado_y_reproducible():
    grupos = [f"d{i // 10}" for i in range(200)]
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 200)
    sa = rng.uniform(0, 1, 200)
    sb = sa * 0.5
    r1 = bootstrap_pareado(grupos, y, {"a": sa, "b": sb}, {"a": 0.5, "b": 0.5}, n_rep=200, semilla=3)
    r2 = bootstrap_pareado(grupos, y, {"a": sa, "b": sb}, {"a": 0.5, "b": 0.5}, n_rep=200, semilla=3)
    assert np.array_equal(r1["a_TNR"], r2["a_TNR"])
    # b descarta más que a en todas las réplicas (mismas réplicas para ambos)
    assert np.all(r1["b_TNR"] >= r1["a_TNR"])
    lo, hi = ic95(r1["a_TNR"])
    assert 0 <= lo <= hi <= 1

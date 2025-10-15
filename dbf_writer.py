from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple, Optional, List, Dict, Any

import dbf


# Field specs copied to match core.integraciones.vfp
MOVIMCAB_SPECS = (
    "CODSUCUR C(2);"
    "TIPO C(2);"
    "FECHA C(8);"
    "BOLETA C(7);"
    "FECHABOL D;"
    "PRIMNROSBO C(6);"
    "CLIPROV C(4);"
    "TIMBRADO C(8);"
    "TIMBRAVENC D;"
    "TOTALIVA N(11,0);"
    "ANTICIREN N(8,0);"
    "TOTALVTA10 N(12,0);"
    "TOTALVTA5 N(12,0);"
    "TOTALEXEN N(12,0);"
    "COSTOFLETE N(13,3);"
    "TOTCOSTODL N(9,2);"
    "VENCIMIENT D;"
    "FECHADESPA D;"
    "NRODESPA C(16);"
    "DESPACHO N(8,0);"
    "VALORFACTU N(12,0);"
    "BASEIMP N(12,0);"
    "TIPOCAMBIO N(5,0);"
    "TOTALKILOS N(9,3);"
    "RETENCION N(8,0);"
    "BOLETARETE C(7);"
    "FECHARETEN C(8);"
    "VENTAS10Y5 N(12,0);"
    "LINEAPRECI C(1);"
    "COMVTAASO C(13);"
    "TIMVTAASO N(8,0);"
    "OPERMONEXT C(1);"
    "ELECTVIRTU C(1);"
    "VENDECLAVE C(2);"
    "FORMAPAGO C(1);"
    "CLIRUC C(9);"
    "CLIDESCRIP C(40);"
    "ULTFILA N(2,0);"
    "REPROCESO C(1);"
    "TARJETA N(2,0);"
    "EMAIL C(40)"
)

MOVIMITE_SPECS = (
    "CLAVE C(19);"
    "ITEM C(2);"
    "CODIGO C(5);"
    "CANTIDAD N(11,3);"
    "PRECIOVENT N(12,3);"
    "PRECIOIVA N(12,3);"
    "PRECIOCOST N(12,3);"
    "PRECIOCODL N(10,5);"
    "PRECIVENDL N(9,4);"
    "TASA N(2,0);"
    "LOTE C(6)"
)


@dataclass(frozen=True)
class ExportStats:
    records: int
    movimcab_bytes: int
    movimite_bytes: int


def _zfill(value: Optional[str], width: int) -> str:
    if value is None:
        return "".zfill(width)
    return str(value).zfill(width)


def _yyyymmdd(date_str: Optional[str]) -> str:
    if not date_str:
        return ""
    # assume YYYY-MM-DD
    return date_str.replace("-", "")


def _tipo_plazo_to_tipo(tipo_plazo: str) -> str:
    if tipo_plazo == "CO":
        return "15"
    if tipo_plazo == "CR":
        return "17"
    return ""


def _numfact(est: str, pto: str, num: Any) -> str:
    if num in (None, ""):
        return ""
    return f"{_zfill(est,3)}-{_zfill(pto,3)}-{_zfill(str(num),7)}"


def _boleta(numero: Any) -> str:
    if numero in (None, ""):
        return ""
    return _zfill(str(numero), 7)[-7:]


def write_dbf_pair(
    facturas: Iterable[Dict[str, Any]],
    movimcab_path: str,
    movimite_path: str,
    codepage: str = "cp1252",
) -> ExportStats:
    # clean conflicting outputs (vfp index/memo)
    for base in (movimcab_path, movimite_path):
        for ext in (".dbf", ".cdx", ".fpt"):
            p = Path(Path(base).with_suffix(ext))
            if p.exists():
                p.unlink()

    movimcab = dbf.Table(
        movimcab_path,
        field_specs=MOVIMCAB_SPECS,
        dbf_type="vfp",
        codepage=codepage,
    )
    movimite = dbf.Table(
        movimite_path,
        field_specs=MOVIMITE_SPECS,
        dbf_type="vfp",
        codepage=codepage,
    )

    count = 0
    movimcab.open(mode=dbf.READ_WRITE)
    movimite.open(mode=dbf.READ_WRITE)
    try:
        for f in facturas:
            est = str(f.get("numero_establecimiento", ""))
            pto = str(f.get("punto_expedicion", ""))
            num = f.get("numero")
            fecha = _yyyymmdd(f.get("fecha"))
            tipo = _tipo_plazo_to_tipo(str(f.get("tipo_plazo", "")))
            codsucur = "EU"
            boleta = _boleta(num)
            # PRIMNROSBO is C(6): last 3 digits of est + last 3 of pto
            est3 = _zfill(est, 3)[-3:]
            pto3 = _zfill(pto, 3)[-3:]
            primnrosbo = f"{est3}{pto3}"[:6]

            cliente = f.get("cliente") or {}
            cliprov = None if tipo == "15" else (str(cliente.get("id_cliente", "")).zfill(4)[-4:] if cliente else None)

            # Totals and dates
            total_iva = int(f.get("total_iva") or 0)
            total_exen = int(f.get("total_exentas") or 0)

            # Compute TOTALVTA10 / TOTALVTA5 from items' subtotal by tasa
            total_vta10 = 0
            total_vta5 = 0
            for _it in (f.get("items") or []):
                tasa_val = int(_it.get("tasa") or 0)
                subtotal_val = int(round((_it.get("subtotal") or 0)))
                if tasa_val == 10:
                    total_vta10 += subtotal_val
                elif tasa_val == 5:
                    total_vta5 += subtotal_val

            # For D fields, pass a date object or None
            vencimiento = None
            v_str = f.get("vencimiento")
            if v_str:
                try:
                    from datetime import datetime
                    vencimiento = datetime.strptime(v_str, "%Y-%m-%d").date()
                except Exception:
                    vencimiento = None
            cliruc = (cliente or {}).get("ruc", "")
            clidescrip = (cliente or {}).get("nombre", "")

            movimcab.append((
                codsucur,            # CODSUCUR C(2)
                tipo,                # TIPO C(2)
                fecha,               # FECHA C(8) yyyymmdd
                boleta,              # BOLETA C(7)
                None,                # FECHABOL D
                primnrosbo,          # PRIMNROSBO C(6)
                cliprov,             # CLIPROV C(4)
                None,                # TIMBRADO C(8)
                None,                # TIMBRAVENC D
                total_iva,           # TOTALIVA N(11,0)
                0,                   # ANTICIREN N(8,0)
                total_vta10,         # TOTALVTA10 N(12,0)
                total_vta5,          # TOTALVTA5 N(12,0)
                total_exen,          # TOTALEXEN N(12,0)
                0.0,                 # COSTOFLETE N(13,3)
                0.0,                 # TOTCOSTODL N(9,2)
                vencimiento,         # VENCIMIENT D
                None,                # FECHADESPA D
                None,                # NRODESPA C(16)
                0,                   # DESPACHO N(8,0)
                0,                   # VALORFACTU N(12,0)
                0,                   # BASEIMP N(12,0)
                0,                   # TIPOCAMBIO N(5,0)
                0.0,                 # TOTALKILOS N(9,3)
                0,                   # RETENCION N(8,0)
                None,                # BOLETARETE C(7)
                None,                # FECHARETEN C(8)
                0,                   # VENTAS10Y5 N(12,0)
                None,                # LINEAPRECI C(1)
                None,                # COMVTAASO C(13)
                0,                   # TIMVTAASO N(8,0)
                None,                # OPERMONEXT C(1)
                "N",                # ELECTVIRTU C(1)
                "BB",               # VENDECLAVE C(2)
                ("N" if tipo == "15" else None),  # FORMAPAGO C(1)
                cliruc,              # CLIRUC C(9)
                clidescrip,          # CLIDESCRIP C(40)
                int(len(f.get("items", []))),  # ULTFILA N(2,0)
                None,                # REPROCESO C(1)
                0,                   # TARJETA N(2,0)
                None,                # EMAIL C(40)
            ))

            # Items
            items: List[Dict[str, Any]] = f.get("items", []) or []
            for item in items:
                producto = item.get("producto") or {}
                clave = f"{codsucur}{tipo}{fecha}{boleta}".ljust(19)[:19]
                item_num = str(item.get("numero_linea", "")).zfill(2)[-2:]
                codigo = producto.get("codigo", "")
                cantidad = float(item.get("cantidad") or 0.0)
                precio_vent = float(item.get("precio_neto") or 0.0)
                precio_iva = float(item.get("precio") or 0.0)
                tasa = item.get("tasa") or 0
                lote = (producto.get("lote") or "")[:6]

                movimite.append((
                    clave,
                    item_num,
                    codigo,
                    cantidad,
                    precio_vent,
                    precio_iva,
                    0,
                    0,
                    0,
                    tasa,
                    lote,
                ))

            count += 1
    finally:
        movimcab.close()
        movimite.close()

    size_cab = Path(movimcab_path).stat().st_size if Path(movimcab_path).exists() else 0
    size_ite = Path(movimite_path).stat().st_size if Path(movimite_path).exists() else 0
    return ExportStats(records=count, movimcab_bytes=size_cab, movimite_bytes=size_ite)



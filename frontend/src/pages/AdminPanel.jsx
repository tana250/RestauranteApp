import { useState } from "react";
import ProveedorNuevo from "../components/Proveedor/ProveedorNuevo";
import ProveedorListar from "../components/Proveedor/ProveedorListar";
import UnidadesMedidaNuevo from "../components/UnidadesMedida/UnidadesMedidaNuevo";
import UnidadesMedidaListar from "../components/UnidadesMedida/UnidadesMedidaListar";
import TiposInsumoNuevo from "../components/TiposInsumo/TiposInsumoNuevo";
import TiposInsumoListar from "../components/TiposInsumo/TiposInsumoListar";
import MarcasNuevo from "../components/Marcas/MarcasNuevo";
import MarcasListar from "../components/Marcas/MarcasListar";
import PersonalNuevo from "../components/Personal/PersonalNuevo";
import PersonalListar from "../components/Personal/PersonalListar";
import MozoNuevo from "../components/Mozo/MozoNuevo";
import MozoListar from "../components/Mozo/MozoListar";
import MesaNuevo from "../components/Mesa/MesaNuevo";
import MesaListar from "../components/Mesa/MesaListar";
import EgresoMercaderiaNuevo from "../components/EgresoMercaderia/EgresoMercaderiaNuevo";
import EgresoMercaderiaListar from "../components/EgresoMercaderia/EgresoMercaderiaListar";
import VentaNuevo from "../components/Venta/VentaNuevo";
import VentaListar from "../components/Venta/VentaListar";
import ProductoVentaNuevo from "../components/ProductoVenta/ProductoVentaNuevo";
import ProductoVentaListar from "../components/ProductoVenta/ProductoVentaListar";
import ConsumoPersonalNuevo from "../components/ConsumoPersonal/ConsumoPersonalNuevo";
import ConsumoPersonalListar from "../components/ConsumoPersonal/ConsumoPersonalListar";
import MetodosPagoNuevo from "../components/MetodosPago/MetodosPagoNuevo";
import MetodosPagoListar from "../components/MetodosPago/MetodosPagoListar";
import PagosNuevo from "../components/Pagos/PagosNuevo";
import PagosListar from "../components/Pagos/PagosListar";
import Productos from "./Productos";
import Mercaderia from "./Mercaderia";

const secciones = [
  { key: "proveedor", label: "Proveedor", Nuevo: ProveedorNuevo, Listar: ProveedorListar },
  { key: "unidadesMedida", label: "Unidades de Medida", Nuevo: UnidadesMedidaNuevo, Listar: UnidadesMedidaListar },
  { key: "tiposInsumo", label: "Tipos de Insumo", Nuevo: TiposInsumoNuevo, Listar: TiposInsumoListar },
  { key: "marcas", label: "Marcas", Nuevo: MarcasNuevo, Listar: MarcasListar },
  { key: "mercaderia", label: "Mercadería", Page: Mercaderia },
  { key: "productos", label: "Productos", Page: Productos },
  { key: "personal", label: "Personal", Nuevo: PersonalNuevo, Listar: PersonalListar },
  { key: "mozo", label: "Mozo", Nuevo: MozoNuevo, Listar: MozoListar },
  { key: "mesa", label: "Mesa", Nuevo: MesaNuevo, Listar: MesaListar },
  { key: "egresoMercaderia", label: "Egreso de Mercadería", Nuevo: EgresoMercaderiaNuevo, Listar: EgresoMercaderiaListar },
  { key: "venta", label: "Venta", Nuevo: VentaNuevo, Listar: VentaListar },
  { key: "productoVenta", label: "Producto Venta", Nuevo: ProductoVentaNuevo, Listar: ProductoVentaListar },
  { key: "consumoPersonal", label: "Consumo Personal", Nuevo: ConsumoPersonalNuevo, Listar: ConsumoPersonalListar },
  { key: "metodosPago", label: "Métodos de Pago", Nuevo: MetodosPagoNuevo, Listar: MetodosPagoListar },
  { key: "pagos", label: "Pagos", Nuevo: PagosNuevo, Listar: PagosListar },
];

export default function AdminPanel() {
  const [activa, setActiva] = useState(secciones[0].key);
  const seccion = secciones.find((s) => s.key === activa);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside style={{ width: "250px", borderRight: "1px solid #ccc", padding: "1rem" }}>
        <h2>Administrador</h2>
        <nav>
          {secciones.map((s) => (
            <button
              key={s.key}
              onClick={() => setActiva(s.key)}
              style={{ display: "block", width: "100%", textAlign: "left", marginBottom: "0.5rem", fontWeight: activa === s.key ? "bold" : "normal" }}
            >
              {s.label}
            </button>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, padding: "1rem" }}>
        <h1>{seccion.label}</h1>
        {seccion.Page ? (
          <seccion.Page />
        ) : (
          <>
            <section style={{ marginBottom: "2rem" }}>
              <h2>Nuevo</h2>
              <seccion.Nuevo />
            </section>
            <section>
              <h2>Listar</h2>
              <seccion.Listar />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

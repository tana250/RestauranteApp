import os

simple = [
  ('UnidadesMedida','unidadesMedida','nombre'),
  ('TiposInsumo','tiposInsumo','tipo'),
  ('Marcas','marcas','nombre'),
  ('Insumos','insumos',None),
  ('IngresoMercaderia','ingresoMercaderia',None),
  ('RecetasProductos','recetasProductos',None),
  ('Mozo','mozo',None),
  ('Mesa','mesa','numero'),
  ('EgresoMercaderia','egresoMercaderia',None),
  ('Venta','venta',None),
  ('ProductoVenta','productoVenta',None),
  ('ConsumoPersonal','consumoPersonal',None),
  ('Pagos','pagos',None),
]

for folder, hook_name, campo in simple:
    path = f'/home/fran/Escritorio/RestauranteApp/frontend/src/components/{folder}'
    os.makedirs(path, exist_ok=True)
    if campo:
        if campo == 'numero':
            nuevo = f'''import {{ useState }} from "react";
import use{folder} from "../../hooks/use{folder}";

export default function {folder}Nuevo({{ onCreated }}) {{
  const {{ create }} = use{folder}();
  const [numero, setNumero] = useState("");

  const handleSubmit = async (e) => {{
    e.preventDefault();
    await create({{ numero: Number(numero) }});
    setNumero("");
    if (onCreated) onCreated();
  }};

  return (
    <form onSubmit={{handleSubmit}}>
      <input type="number" value={{numero}} onChange={{(e) => setNumero(e.target.value)}} placeholder="numero" required />
      <button type="submit">Guardar</button>
    </form>
  );
}}
'''
        else:
            nuevo = f'''import {{ useState }} from "react";
import use{folder} from "../../hooks/use{folder}";

export default function {folder}Nuevo({{ onCreated }}) {{
  const {{ create }} = use{folder}();
  const [{campo}, set{campo.capitalize()}] = useState("");

  const handleSubmit = async (e) => {{
    e.preventDefault();
    await create({{ {campo} }});
    set{campo.capitalize()}("");
    if (onCreated) onCreated();
  }};

  return (
    <form onSubmit={{handleSubmit}}>
      <input value={{{campo}}} onChange={{(e) => set{campo.capitalize()}(e.target.value)}} placeholder="{campo}" required />
      <button type="submit">Guardar</button>
    </form>
  );
}}
'''
    else:
        nuevo = f'''import {{ useState }} from "react";
import use{folder} from "../../hooks/use{folder}";

export default function {folder}Nuevo({{ onCreated }}) {{
  const {{ create }} = use{folder}();
  const [json, setJson] = useState("{{}}");

  const handleSubmit = async (e) => {{
    e.preventDefault();
    try {{
      const data = JSON.parse(json);
      await create(data);
      setJson("{{}}");
      if (onCreated) onCreated();
    }} catch (err) {{
      alert("JSON invalido");
    }}
  }};

  return (
    <form onSubmit={{handleSubmit}}>
      <textarea value={{json}} onChange={{(e) => setJson(e.target.value)}} placeholder='{{"campo":"valor"}}' />
      <button type="submit">Guardar</button>
    </form>
  );
}}
'''
    with open(f'{path}/{folder}Nuevo.jsx','w') as f:
        f.write(nuevo)
    
    listar = f'''import use{folder} from "../../hooks/use{folder}";

export default function {folder}Listar({{ onEdit }}) {{
  const {{ items, remove }} = use{folder}();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Datos</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {{items.map((item) => (
          <tr key={{item.id}}>
            <td>{{item.id}}</td>
            <td><pre>{{JSON.stringify(item)}}</pre></td>
            <td>
              <button onClick={{() => onEdit && onEdit(item)}}>Editar</button>
              <button onClick={{() => remove(item.id)}}>Eliminar</button>
            </td>
          </tr>
        ))}}
      </tbody>
    </table>
  );
}}
'''
    with open(f'{path}/{folder}Listar.jsx','w') as f:
        f.write(listar)

print('done')

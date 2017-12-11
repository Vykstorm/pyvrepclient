
-- Este script debe ser incluido en la escena V-rep para trabajar con esta librería de forma remota.
-- El script debe estar en modo "non-threaded" y debe estar asociado a un objeto de la escena de
-- llamado "ScriptHandler" (es un objeto de tipo "dummy")

json = require('dkjson')

function_proxy = function(inInts,inFloats,inStrings,inBuffer)
    function_name = inStrings[1]
    function_args = json.decode(inStrings[2])
    func = _G[function_name]
    result = json.encode({func(unpack(function_args))})

	return {},{},{result},''
end


function get_objects_info()
    object_types = {sim_object_shape_type, sim_object_joint_type,
    sim_object_proximitysensor_type, sim_object_visionsensor_type}

    local objects_info = {}
    for _, object_type in ipairs(object_types) do
        local object_handles = simGetObjectsInTree(sim_handle_scene, object_type, 1)
        for _, object_handle in ipairs(object_handles) do
            local object_name = simGetObjectName(object_handle)
            table.insert(objects_info, {object_handle, object_name, object_type})
        end
    end
    return objects_info
end


-- Este código es incluido para que al iniciar la simulación esta se pause automáticamente, para poder ejecutar
-- remotamente las funciones de este script sin que la simulación este activa. El cliente posteriormente puede
-- resumir la simulación.
if (sim_call_type==sim_childscriptcall_initialization) then
    simPauseSimulation()
end

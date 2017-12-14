
-- Este script debe ser incluido en la escena V-rep para trabajar con esta librería de forma remota.
-- El script debe estar en modo "non-threaded" y debe estar asociado a un objeto de la escena de
-- llamado "ScriptHandler" (es un objeto de tipo "dummy")


-- Las siguientes líneas de código establecen la velocidad de los motores de la escena a 0 al comenzar
-- la simulación.
if (sim_call_type==sim_childscriptcall_initialization) then
    joints = simGetObjectsInTree(sim_handle_scene, sim_object_joint_type, 1)
    for _, joint in ipairs(joints) do
        simSetJointTargetVelocity(joint, 0)
    end
end
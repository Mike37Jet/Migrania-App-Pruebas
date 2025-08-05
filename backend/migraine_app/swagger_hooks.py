def custom_preprocessing_hook(endpoints):
    """
    Hook de preprocesamiento para organizar endpoints
    """
    filtered = []
    
    for (path, path_regex, method, callback) in endpoints:
        filtered.append((path, path_regex, method, callback))
    
    return filtered

def custom_postprocessing_hook(result, generator, request, public):
    """
    Hook de postprocesamiento para modificar el schema final
    """
    # Organizar endpoints por path
    if 'paths' in result:
        for path, path_obj in result['paths'].items():
            for method, operation in path_obj.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    
                    # Endpoints de autenticación
                    if '/api/auth/' in path:
                        operation['tags'] = ['🔐 Autenticación']
                    
                    # Endpoints de usuarios
                    elif '/api/usuarios/' in path:
                        operation['tags'] = ['👥 Usuarios']
                    
                    # Endpoints de registro
                    elif any(reg_path in path for reg_path in ['/registro-medico/', '/registro-paciente/', '/registro-enfermera/']):
                        operation['tags'] = ['📝 Registro']
                    
                    # Endpoints de evaluación y diagnóstico
                    elif '/api/evaluaciones/' in path or '/bitacora/' in path:
                        operation['tags'] = ['📋 Evaluación y diagnóstico']
                        
                    # Endpoints de tratamiento
                    elif '/api/tratamientos/' in path:
                        operation['tags'] = ['💊 Tratamiento']
                    
    
    return result
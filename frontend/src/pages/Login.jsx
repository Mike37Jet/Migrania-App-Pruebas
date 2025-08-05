import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeSlash } from '@phosphor-icons/react';
import styles from '../common/styles/Login.module.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // 1. Obtener el token de autenticación
      const loginResponse = await fetch(
        'http://127.0.0.1:8000/api/auth/jwt/create/',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        }
      );

      if (!loginResponse.ok) {
        throw new Error('Las credenciales proporcionadas son incorrectas.');
      }

      const tokenData = await loginResponse.json();

      localStorage.setItem('access', tokenData.access);
      localStorage.setItem('refresh', tokenData.refresh);

      // 2. Obtener la información del dashboard para la redirección
      const dashboardResponse = await fetch(
        'http://127.0.0.1:8000/api/usuarios/dashboard/',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${tokenData.access}`,
          },
        }
      );

      if (!dashboardResponse.ok) {
        throw new Error('No se pudo obtener la información del dashboard.');
      }

      const dashboardData = await dashboardResponse.json();
      const userRole = dashboardData.tipo_usuario;

      // 3. Redirigir basado en el rol del usuario
      if (userRole === 'paciente') {
        navigate('/dashboard-paciente');
      } else if (userRole === 'medico') {
        navigate('/dashboard-medico');
      } else if (userRole === 'enfermera') {
        navigate('/dashboard-enfermera');
      } else {
        navigate('/');
      }
    } catch (err) {
      console.error('Error en el proceso de inicio de sesión:', err.message);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNavigateToRegister = () => {
    navigate('/registroApp');
  };

  return (
    <div className={styles['login']}>
      <div className={styles['login__tarjeta']}>
        <h1 className={styles.login__titulo}>Bienvenido de nuevo</h1>

        <form
          onSubmit={handleSubmit}
          className={styles['login__formulario']}
        >
          <div className={styles['login__grupo-input']}>
            <label htmlFor='email'>Dirección de correo electrónico</label>
            <input
              type='email'
              id='email'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder='Por ejemplo: john@company.com'
              required
              disabled={isLoading}
            />
          </div>

          <div className={styles['login__grupo-input']}>
            <label htmlFor='password'>Contraseña</label>
            <div className={styles['login__contenedor-password']}>
              <input
                type={showPassword ? 'text' : 'password'}
                id='password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder='Más de 12 caracteres'
                required
                disabled={isLoading}
              />
              <span
                className={styles['login__icono-password']}
                onClick={() => !isLoading && setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeSlash size={22} /> : <Eye size={22} />}
              </span>
            </div>
          </div>

          <button
            type='submit'
            className={styles['login__boton']}
            disabled={isLoading}
          >
            {isLoading ? 'Iniciando...' : 'Iniciar sesión'}
          </button>
          {error && <p className={styles.login__mensaje_error}>{error}</p>}
        </form>
        <button
          type='button'
          onClick={handleNavigateToRegister}
          className={styles.login__boton}
          disabled={isLoading}
        >
          Registrarse
        </button>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeSlash } from '@phosphor-icons/react';
import styles from '../styles/Login.module.css';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log("Intentando iniciar sesión con:", { email, password });

    };

    return (
        <div className={styles["login"]}>
            <div className={styles["login__tarjeta"]}>
                <h1 className={styles.login__titulo}>Bienvenido de nuevo</h1>

                <form onSubmit={handleSubmit} className={styles["login__formulario"]}>
                    <div className={styles["login__grupo-input"]}>
                        <label htmlFor="email">Dirección de correo electrónico</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Por ejemplo: john@company.com"
                            required
                        />
                    </div>

                    <div className={styles["login__grupo-input"]}>
                        <label htmlFor="password">Contraseña</label>
                        <div className={styles["login__contenedor-password"]}>
                            <input

                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Más de 12 caracteres"
                                required
                            />

                            <span
                                className={styles["login__icono-password"]}
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeSlash size={22} /> : <Eye size={22} />}
                            </span>
                        </div>
                    </div>

                    <button type="submit" className={styles["login__boton"]}>
                        Iniciar sesión
                    </button>
                </form>
                <Link to="/analisis-patrones" className={styles.login__boton}>
                    Registrarse
                </Link>
            </div>
        </div>
    );
}
// Importazione di Formik per la gestione del form
import { useFormik } from "formik";
import React, { useContext, useEffect, useState } from "react";
// Importazione della libreria Yup per la validazione
import { object, string, date } from "yup";
// Importazione del contesto globale dell'applicazione
import { StateContext } from "../../App";
// Importazione del componente per la gestione degli errori
import { ErrorMessage } from "../ErrorMessage";
// Importazione delle etichette e messaggi utilizzati nei campi del form
import { CAMPO_OBBLIGATORIO, REQUIRED_FIELD, REQUIRED_FIELD_BOOLEAN } from "../labels";
// Importazione dello schema di validazione dei campi del form
import { validationSchema } from "./ValidationSchema";
// Importazione delle funzioni di routing
import { BrowserRouter, Route, RouterProvider, Routes, 
  createBrowserRouter, useNavigate } from "react-router-dom";


// Tipo dei valori del form
export type TFormValues = { username: string; password: string; };
// Tipo degli errori del form
export type TFormErrors = TFormValues;



// Funzione principale del componente per il modulo di login
export function LoginForm() {
const navigate = useNavigate(); // Hook per la navigazione tra le pagine
const [errorMessage, setErrorMessage] = useState(""); // Stato per memorizzare i messaggi di errore
const { dispatch } = useContext(StateContext); // Accesso allo stato globale tramite il contesto
  
// Esegui l'effetto quando il componente viene montato
useEffect(() => {

  // Controlla se il token JWT è presente nel localStorage
  const jwt = localStorage.getItem("jwt");
  // Naviga alla homepage se l'utente è autenticato
  if (jwt) navigate("/");
}, []);   // L'effetto viene eseguito solo una volta al montaggio

  // Configurazione di Formik per la gestione del form e la validazione
const formik = useFormik({
  initialValues: {
    username: "", // Valore iniziale per il campo username
    email: "", // Valore iniziale per il campo email
    password: "", // Valore iniziale per il campo password
    termsofuse: false, // Valore iniziale per il checkbox termini d'uso
  },


  validationSchema: validationSchema, // Schema Yup per la validazione del form
  validateOnChange: true, // Esegui la validazione a ogni modifica
  validateOnBlur: true, // Esegui la validazione quando un campo perde il focus

    // Funzione da eseguire al submit del form
  onSubmit: (values) => {

    // Effettua una richiesta POST per autenticare l'utente
    fetch("https://dummyjson.com/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" }, // Imposta il tipo di contenuto
      body: JSON.stringify({
        username: values.username, // Passa l'username del form
        password: values.password, // Passa la password del form
      }),
    })
      .then((res) => res.json()) // Converte la risposta in JSON
      .then((res) => {
        if (res.token) { // Se la risposta contiene un token
          localStorage.setItem("jwt", res.token); // Memorizza il token nel localStorage
          navigate("/"); // Naviga alla homepage
        } else {
          setErrorMessage(res.message); // Imposta un messaggio di errore
        }
      });
  },
});


// Ritorna il modulo di login come JSX
  return (
      <form className="login-panel" onSubmit={formik.handleSubmit}>
<h2 className="titleH2">Welcome!</h2>
            <p className="paragraph">Enter your login details:</p>
            
            <div className="riga-form-login">
              <label htmlFor="username" className="form-label left">Username</label>

 {/* Campo per l'username */}
        <input
          id="username"
          placeholder="username"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        /> {/* Mostra il messaggio di errore per il campo username */}
        {formik.errors.username && formik.touched.username ? (
          <ErrorMessage message={formik.errors.username} isError={false} />
        ) : null}
        </div>
  
  {/* Campo per la password */}
        <div className="riga-form-login">
              <label htmlFor="password" className="form-label left">Password</label>

{/* Mostra il messaggio di errore per il campo password */}
        <input
          id="password"
          placeholder="password"
          type="password"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        {formik.errors.password && formik.touched.password ? (
          <ErrorMessage message={formik.errors.password} isError={false} />
        ) : null}
</div>

{/* Checkbox per i termini d'uso */}
<div className="checkbox-login">
<label htmlFor="termsofuse" className="form-label-termsofuse">I accept the terms of use</label>
<input
id="checkbox-login"
type="checkbox"
onChange={formik.handleChange}
onBlur={formik.handleBlur}
/>
{formik.errors.termsofuse  && formik.touched.termsofuse ? (
            <ErrorMessage message={formik.errors.termsofuse} isError={false} />  
            ) : null}
</div>

  {/* Pulsante di invio del form */}
        <div className="div-btn">
                <button type="submit" className="btn" onClick ={() => navigate("/")}>Log in</button>
            </div>
            
            {/* Collegamento alla pagina di registrazione */}
            <div className="register-access">
              <span>Don't have an account? </span> 
              <a href="" onClick ={() => navigate("/signup")}>Sign Up</a>
              
              </div>

      
      
      </form>
    );
}


import React, { createContext, useEffect, useReducer } from "react";
import {
  BrowserRouter,
  Route,
  RouterProvider,
  Routes,
  createBrowserRouter,
  useNavigate,
} from "react-router-dom";
import "./app.css";
import { Dashboard } from "./components/Dashboard";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { LoginForm } from "./components/LoginForm/LoginForm";
import { PrivateRoute } from "./components/PrivateRoute";
import { Signup } from "./components/SignUp/SignUp";
import { useFetchData } from "./hooks/useFetchData";
import { reducer } from "./state/reducer";
import { BookDetails } from "./components/BookDetails";

type TUsers = { 
  id: string; 
  name: string; 
  email: string 
};

// Creazione del contesto globale per lo stato dell'applicazione
export const StateContext = createContext<{
  username: string;
  dispatch: React.Dispatch<any>;
} | null>(null);

// devo creare un'istanza del router. Dentro passo un array di oggetti con i componenti che devo fare vedere e le rispettive rotte
// CreateBrowserRouter: It uses the DOM History API to update the URL and manage the history stack.
const router = createBrowserRouter([
  {
    path: "/", // Rotta per la dashboard protetta da autenticazione
    element: (
      <PrivateRoute>
        <Dashboard />
      </PrivateRoute>
    ),
  },
  {
    path: "/details", // Rotta per i dettagli del libro/professionista, anche questa protetta
    element: (
      <PrivateRoute>
        <BookDetails />
      </PrivateRoute>
    ),
  },
  { 
    path: "/login", // Rotta per il modulo di login
    element: <LoginForm />,
  },
  {
    path: "/signup", // Rotta per il modulo di registrazione
    element: <Signup />,
  },
]);


// Funzione principale del componente dell'app
export function App(props: { title: string }) {
  // const [users, setUsers] = useState<TUsers[]>([]);
  // useEffect(() => {
  //   fetch("http://localhost:3000/users")
  //     .then((res) => res.json())
  //     .then((users) => setUsers(users));
  // }, []);

  // Gestione dello stato dell'applicazione con useReducer
  const [appState, dispatch] = useReducer(reducer, { username: "" });

  // const data = useFetchData();

    // Ritorna la struttura dell'applicazione come JSX
  return (
    <div className="app">
      {/* Intestazione dell'app con titolo passato come proprietà */}
      <Header title={props.title} />
      <div className="content">
        <StateContext.Provider
          value={{
            username: appState.username,
            dispatch,
          }}
        >
          {/* RouterProvider per gestire il routing tra le pagine */}
          <RouterProvider router={router} />
        </StateContext.Provider>
      </div>





      <Footer />
    </div>
  );
}
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
import { Signup } from "./components/Signup";
import { useFetchData } from "./hooks/useFetchData";
import { reducer } from "./state/reducer";
import { BookDetails } from "./components/BookDetails";

type TUsers = { id: string; name: string; email: string };

export const StateContext = createContext<{
  username: string;
  dispatch: React.Dispatch<any>;
} | null>(null);

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <PrivateRoute>
        <Dashboard />
      </PrivateRoute>
    ),
  },
  {
    path: "/details",
    element: (
      <PrivateRoute>
        <BookDetails />
      </PrivateRoute>
    ),
  },
  {
    path: "/login",
    element: <LoginForm />,
  },
  {
    path: "/signup",
    element: <Signup />,
  },
]);

export function App(props: { title: string }) {
  // const [users, setUsers] = useState<TUsers[]>([]);
  // useEffect(() => {
  //   fetch("http://localhost:3000/users")
  //     .then((res) => res.json())
  //     .then((users) => setUsers(users));
  // }, []);

  const [appState, dispatch] = useReducer(reducer, { username: "" });

  const data = useFetchData();

  return (
    <div className="app">
      <Header title={props.title} />
      <div className="content">
        <StateContext.Provider
          value={{
            username: appState.username,
            dispatch,
          }}
        >
          <RouterProvider router={router} />
        </StateContext.Provider>
      </div>





      <Footer />
    </div>
  );
}
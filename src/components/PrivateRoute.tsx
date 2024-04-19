import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

export function PrivateRoute({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const jwt = useMemo(() => localStorage.getItem("jwt"), []);

  useEffect(() => {
    if (!jwt) {
      navigate("/login");
    }
  }, [jwt]);

  if (!jwt) {
    return null;
  } else {
    return children;
  }
}

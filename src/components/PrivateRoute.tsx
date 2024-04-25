import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function PrivateRoute({ children }: { children: React.ReactNode }) {
    
    const isAuthenticated = true
    const navigate = useNavigate();
    
    
    useEffect(() => {
      if (!isAuthenticated) {
        navigate("/login");
      }
    }, []);
  
    if (!isAuthenticated) {
      return null;
    } else {
      return children;
    }
  }
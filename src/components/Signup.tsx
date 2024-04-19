import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { StateContext } from "../App";

export function Signup() {
  const navigate = useNavigate();
  const { dispatch } = useContext(StateContext);
  const [formValues, setFormValues] = useState({
    nome: "",
    cognome: "",
    gender: "Altro",
    isMarried: true,
    email: "",
    username: "",
    password: "",
    conferma: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch({ type: "UPDATE_USERNAME", payload: formValues.username });
    navigate("/");
  };

  const handleChange = (e) => {
    const value = e.target.value;
    const id = e.target.id;
    setFormValues((prevState) => ({ ...prevState, [id]: value }));
  };

  const handleBlur = () => {};

  const handleCheckboxChange = (e) => {
    const checked = e.target.checked;
    const id = e.target.id;
    setFormValues((prevState) => ({ ...prevState, [id]: checked }));
  };

  return (
    <form className="login-panel" onSubmit={handleSubmit}>
      <h2>Sign Up</h2>
      <input
        id="nome"
        placeholder="nome"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <input
        id="cognome"
        placeholder="cognome"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <select id="gender" value={formValues.gender} onChange={handleChange}>
        <option value={"Uomo"}>Uomo</option>
        <option value={"Donna"}>Donna</option>
        <option value={"Altro"}>Altro</option>
      </select>
      <label htmlFor="isMarried">Is married?</label>
      <input
        id="isMarried"
        type="checkbox"
        checked={formValues.isMarried}
        onChange={handleCheckboxChange}
        placeholder="asda"
      />
      <input
        id="email"
        placeholder="email"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <input
        id="username"
        placeholder="username"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <input
        id="password"
        placeholder="password"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <input
        id="conferma"
        placeholder="conferma"
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <button type="submit" className="submit-button">
        submit
      </button>
    </form>
  );
}

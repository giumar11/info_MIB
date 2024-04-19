import React, { useState, useContext } from "react";
import { BrowserRouter, Route, RouterProvider, Routes, createBrowserRouter, useNavigate } from "react-router-dom";
import { StateContext } from "../../App";
import { ErrorMessage } from "../ErrorMessage";
import { GiArchiveRegister } from "react-icons/gi";
import { REQUIRED_FIELD_BOOLEAN } from "../labels";
import { REQUIRED_FIELD } from "../labels";
import { MATCH_PASSWORD } from "../labels";
import { Form, useFormik } from "formik";
import { validationSchema } from "./ValidationSchema";
import { object, string, date } from "yup";
import YUP from "yup";

export function Signup() {

  const navigate = useNavigate();

  const { dispatch } = useContext(StateContext);

  
  const formik = useFormik ({
    initialValues: {
   
    name: "",
    lastname: "",
    genderassigned: "",
    genderselfidentified: "",
    age: "",
    citizenship: "",
    ethnicity: "",
    username: "",
    email: "",
    password: "",
    confirmpassword: "",
    termsconditions: true,
  },

  validationSchema: validationSchema,

  validateOnChange: true,

  validateOnBlur: true,

  onSubmit:(values) => {
    dispatch({
      type: "UPDATE_USERNAME", payload: values.username,
    });

    fetch ("https://jsonplaceholder.typicode.com/posts", 
    {
      method: "POST",
      body: JSON.stringify(values),
     });

    navigate("/");
  }});

  

  


  return (

    <form 
    id="contact-form"
    className="login-panel" onSubmit={formik.handleSubmit}>

      <h2 className="titleSignup">Sign Up</h2>
      <p className="paragraphSignup">Please, fill in the form to sign up:</p>

      <div className="col">

        <div className="riga-form-register">
          <label htmlFor="name" className="form-label left">Name:</label>
          <input
            id="name"
            name="your-name"
            className="form-control name right"
            placeholder="Enter your name"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.name && formik.touched.name ? (
            <ErrorMessage message={formik.errors.name} isError={false} />
          ) : null}
        </div>

        <div className="riga-form-register">
          <label htmlFor="lastname" className="form-label left">Lastname:</label>
          <input
            id="lastname"
            className="form-control lastname"
            placeholder="Enter your lastname"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.lastname && formik.touched.lastname ? (
            <ErrorMessage message={formik.errors.lastname} isError={false} />
          ) : null}
        </div>

      </div>

      <div className="col">
        <div className="riga-form-register">
          <label htmlFor="genderassigned" className="form-label left">Gender assigned at birth:</label>
          <select
            id="genderassigned"
            className="form-control genderassigned"
            defaultValue="Choose an option"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          >

            <option value="" hidden>Choose an option</option>
            <option value={"Female"}>Female</option>
            <option value={"Male"}>Male</option>
            <option value={"Other"}>Other</option>

          </select>

          {formik.errors.genderassigned && formik.touched.genderassigned ? (
            <ErrorMessage message={formik.errors.genderassigned} isError={false} />
          ) : null}
        </div>


        <div className="riga-form-register">
          <label htmlFor="genderselfidentified" className="form-label left">Gender self-identified:</label>
          <select
            id="ggenderselfidentified"
            className="form-control genderselfidentified"
            defaultValue="Choose an option"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          >

            <option value="" hidden>Choose an option</option>
            <option value={"Female"}>Female</option>
            <option value={"Male"}>Male</option>
            <option value={"Nonbinary"}>Non-binary</option>
            <option value={"Other"}>Other</option>

          </select>

          {formik.errors.genderselfidentified && formik.touched.genderselfidentified ? (
            <ErrorMessage message={formik.errors.genderselfidentified} isError={false} />
          ) : null}
        </div>

      </div>

      <div className="col">

        <div className="riga-form-register">
          <label htmlFor="age" className="form-label left">Age:</label>
          <input
            id="age"
            className="form-control age"
            placeholder="Enter your age"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.age && formik.touched.age ? (
            <ErrorMessage message={formik.errors.age} isError={false} />
          ) : null}
        </div>

      </div>

      <div className="col">
        <div className="riga-form-register">
          <label htmlFor="citizenship" className="form-label left">Citizenship:</label>
          <input
            id="citizenship"
            className="form-control citizenship"
            placeholder="Enter your citizenship"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.citizenship && formik.touched.citizenship ? (
            <ErrorMessage message={formik.errors.citizenship} isError={false} />
          ) : null}
        </div>


        <div className="riga-form-register">
          <label htmlFor="ethnicity" className="form-label left">Ethnicity:</label>
          <input
            id="ethnicity"
            className="form-control ethnicity"
            placeholder="Enter your ethnicity"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.ethnicity && formik.touched.ethnicity ? (
            <ErrorMessage message={formik.errors.ethnicity} isError={false} />
          ) : null}
        </div>

      </div>

      <div className="col">
        <div className="riga-form-register">
          <label htmlFor="username" className="form-label left">Username:</label>
          <input
            id="username"
            className="form-control username"
            placeholder="Enter your username"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.username && formik.touched.username ? (
            <ErrorMessage message={formik.errors.username} isError={false} />
          ) : null}
        </div>

        <div className="riga-form-register">
          <label htmlFor="email" className="form-label left">Email:</label>
          <input
            id="email"
            name="your-email"
            className="form-control email"
            placeholder="Enter your email"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur} />
          {formik.errors.email && formik.touched.email ? (
            <ErrorMessage message={formik.errors.email} isError={false} />
          ) : null}
        </div>
      </div>

      <div className="col">
      <div className="riga-form-register">
        <label htmlFor="password" className="form-label left">Password:</label>
        <input
          id="password"
          className="form-control password"
          placeholder="Enter your password"
          type="password"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur} />
        {formik.errors.password && formik.touched.password ? (
          <ErrorMessage message={formik.errors.password} isError={false} />
        ) : null}
      </div>

      <div className="riga-form-register">
        <label htmlFor="confirmpassword" className="form-label left">Confirm your password:</label>
        <input
          id="confirmpassword"
          className="form-control confirmpassword"
          placeholder="Enter your password"
          type="password"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur} />
        {formik.errors.confirmpassword && formik.touched.confirmpassword ? (
          <ErrorMessage message={formik.errors.confirmpassword} isError={false} />
        ) : null}
      </div>
    </div>

    <div className="col">
    <div className="riga-form-register">
    <input id="termsconditions" type="checkbox" name="generic"
      onChange={formik.handleChange} 
      onBlur = {formik.handleBlur} 
    />
    I've read the <a href="#">Privacy Policy</a> and 
accept the <a href="#">Terms and Conditions</a>

{formik.errors.termsconditions  && formik.touched.termsconditions ? (
            <ErrorMessage message={formik.errors.termsconditions} isError={false} />  
            ) : null}

</div>



<div className="riga-form-register">
  <input type="checkbox" name="newsletter" 
  onChange={formik.handleChange} 
  onBlur = {formik.handleBlur} 
/>
  
  Send me information about products, services, 
deals or recommendations by email (optional)
</div>
</div>
    
    <div className="div-btn">
        <button id="contact-submit" type="submit" className="btn">Submit</button>
      </div>


   
      

</form>





  );
    }
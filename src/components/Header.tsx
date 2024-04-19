import React from "react";
import logo from "./Logos/logo-viola.png"




export function Header(props: { title: string }) {


  return (
    
    <><div className="header">


      <img src={logo} />


    </div>
    
    <div className="payoff">

        <h2 className="titleH2">The first platform to take care of your sexual and reproductive health, daily.</h2>
      </div></>
    
  );
}

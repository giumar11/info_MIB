//useState: hook permette di aggiungere lo stato React a componenti funzionali. Viene utilizzato per dichiarare una variabile di stato (remoteData) e una funzione per aggiornarla (setRemoteData).
//useEffect: hook permette di eseguire effetti collaterali in componenti funzionali, simili ai metodi del ciclo di vita in classi
import { useEffect, useState } from "react";

export function useFetchData() {
  const [remoteData, setRemoteData] = useState();
  //chiama una API esterna per ottenere dati.
  useEffect(() => {
    fetch("https://rickandmortyapi.com/api/character/105")
      .then((res) => res.json())
      .then((data) => setRemoteData(data));
  }, []);


//hook restituisce il valore attuale di remoteData, permettendo a qualsiasi componente che usa questo hook di accedere ai dati remoti ottenuti.
  return remoteData;
}

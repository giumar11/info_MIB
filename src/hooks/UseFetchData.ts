import { useState, useEffect } from "react";

export function useFetchData() {
    const [remoteData, setRemoteData] = useState();
    useEffect(() => {
      fetch("https://rickandmortyapi.com/api/character/105")
        .then((res) => res.json())
        .then((data) => setRemoteData(data));
    }, []);
  
    return remoteData;
  }
import React, { useContext, useEffect, useMemo, useState, ChangeEvent } from "react";
import { StateContext } from "../App";
import { useNavigate } from "react-router-dom";

// Tipo di dato per rappresentare le informazioni dei libri, da cambiare con info richieste a professionist*
type TData = { 
  id: string; 
  cover_image: string; 
  title: string; 
  author: string; 
  publication_year: string; 
  genre: string; 
  description: string 
}

// Funzione principale del componente per la dashboard
export function Dashboard() {

  // Stato per memorizzare il nome dell'utente
  const [name, setName] = useState("");
  // Stato per memorizzare i dati dei libri/professionist*
  const [data, setData] = useState<TData[]>([]);
  // Stato per il genere/specializzazione professionist* selezionato/a
  const [selectedGenre, setSelectedGenre] = useState();
  // Hook per la navigazione tra le pagine
  const navigate = useNavigate();
  // Stato per tracciare lo stato della richiesta di dati
  const [status, setStatus] = useState<
    "IDLE" | "LOADING" | "SUCCESS" | "ERROR"
  >("IDLE");

    // Effettua una richiesta per ottenere i dati dei libri/professionist* al montaggio del componente
  useEffect(() => {

    // Imposta lo stato su "LOADING" durante il caricamento
    setStatus("LOADING");
    fetch("https://freetestapi.com/api/v1/books")
      .then((res) => {
        if (res.status === 200) {
          return res.json(); // Restituisce i dati se la risposta è corretta
        }
        throw new Error("Something went wrong"); // Genera un errore in caso contrario
      })
      .then((data) => {
        setStatus("SUCCESS"); // Imposta lo stato su "SUCCESS" al completamento con successo
        setData(data); // Salva i dati ricevuti nello stato
      })
      .catch((err) => {
        setStatus("ERROR"); // Imposta lo stato su "ERROR" in caso di errore
        console.error(err); // Stampa l'errore nel console log
      });
  }, []); // L'effetto viene eseguito solo una volta al montaggio


  // Gestisce il cambio del genere/specializzazione selezionato/a nell'interfaccia utente
  const handleGenreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // Imposta il genere selezionato nello stato
    setSelectedGenre(e.target.value);
  };

  // flatMap(): per mappare ogni elemento dell'array data in un array di generi.
  // new Set(): per rimuovere i duplicati dal nuovo array generato.
  // useMemo is a React Hook that lets you cache the result of a calculation between re-renders.

  // Usa useMemo per memorizzare i generi unici disponibili nei dati ricevuti
  const options = useMemo(() => {
    // Crea un array con i generi disponibili
      return data.map((item) => item.genre)
    }, [data]) // Dipende dai dati dei libri


    // Ritorna l'interfaccia utente per la dashboard come JSX
  return (


    <>
    
      {/* Messaggio di benvenuto per l'utente */}
    <div className="welcome-user">
      Welcome to Geen.ai, {name} </div>
      
      <div className="container">

{/* Condizionalmente mostra contenuto basato sullo stato */}
        {status === "SUCCESS" ? (


          <><div className="select-option">
            <p>Select a SRH professional:</p>
           
           {/* Dropdown per la selezione del genere/specializzazione */}
            <select className="select-field" 
              value={selectedGenre}
              onChange={handleGenreChange}>

              <option value="">All</option>
              {/* Mostra i generi disponibili come opzioni nel dropdown */}
              {[...options].sort().map(genre => (
                <option key={genre} value={genre}> {genre} </option>
              ))}
            </select>

{/* Mostra la lista dei libri/professionist* disponibili */}
          </div><div className="bookshelf">
              {data.map((item) => {
                // Filtra i libri per il genere/specializzazione selezionato, se presente
                if (!selectedGenre || item.genre.includes(selectedGenre)) {
                  return (
                    <div
                      className="book"
                      key={item.id}
                      // Naviga alla pagina dei dettagli del libro quando viene cliccato
                      onClick={() => navigate(`/details?id=${item.id}`)}>

                      {/* Mostra l'immagine di copertina */}
                      <div className="image-space">
                        <img className="book-cover" src={item.cover_image} />
                      </div>

                      {/* Mostra le informazioni del libro/professionista */}
                      <div>
                        <div className="testo">
                          <b>Titolo:</b> {item.title}
                        </div>
                        <div className="testo">
                          <b>Autore:</b> {item.author}
                        </div>
                        <div className="testo">
                          <b>Anno:</b> {item.publication_year}
                        </div>
                        <div className="testo">
                          <b>Genere:</b> {item.genre[0]}, {item.genre[1]}
                        </div>
                        <div className="testo">
                          <b>Descrizione:</b> {item.description}
                        </div>
                      </div>
                    </div>
                  );
                }

              })}

            </div></>


// Mostra un messaggio di errore se c'è stato un errore nella richiesta
        ) : status === "ERROR" ? (

          <div>Ops...something went wrong</div>
// Mostra un loader mentre i dati vengono caricati
        ) : status === "LOADING" ? (
          <div className="loader"> <p className="loader-text">LOADING...</p></div>
        ) : null}


      </div></>


  );
}


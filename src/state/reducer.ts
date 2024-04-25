// La gestione dello stato è cruciale in React per mantenere l'interfaccia utente sincronizzata con i dati sottostanti
// Un "reducer" è una funzione che prende lo stato corrente dell'applicazione e un'azione (che descrive cosa cambiare), e restituisce un nuovo stato modificato. 

// N.B.: state e action sono ancora da tipicizzare, per ora li ho lasciati con any
export function reducer(state: any, action: {type: any; payload: any;}) {
  
  //Crea una copia dello stato attuale. Questo è importante per non modificare direttamente lo stato originale, mantenendo la funzione pura (non ha effetti collaterali e lo stesso input produce sempre lo stesso output).
  const draft = { ...state };
  
  // Se il tipo di azione è "UPDATE_USERNAME", modifica il campo username del draft (stato copiato) con il nuovo valore specificato in action.payload.
  switch (action.type) {
    case "UPDATE_USERNAME":
      draft.username = action.payload;
      break;
  }

  //Dopo aver apportato tutte le modifiche necessarie al draft, la funzione restituisce il nuovo stato. 
  return draft;
}

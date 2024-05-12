import React, { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const initialNewComment = {
  id: "",
  name: "",
  email: "",
  body: "",
};

export function BookDetails() {
  const { search } = useLocation();
  const query = new URLSearchParams(search);

  const [book, setBook] = useState();
  const [comments, setComments] = useState<Array<unknown>>([]);

  const [newComment, setNewComment] = useState<{
    id: string;
    name: string;
    email: string;
    body: string;
  }>(initialNewComment);

  const [status, setStatus] = useState<
    "IDLE" | "LOADING" | "SUCCESS" | "ERROR"
  >("IDLE");

  useEffect(() => {
    setStatus("LOADING");
    fetch(`https://freetestapi.com/api/v1/books/${query.get("id")}`)
      .then((res) => {
        if (res.status === 200) {
          return res.json();
        }
        throw new Error("Something went wrong");
      })
      .then((data) => {
        setStatus("SUCCESS");
        setBook(data);
      })
      .catch((err) => {
        setStatus("ERROR");
        console.error(err);
      });
  }, []);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/comments")
      .then((res) => {
        if (res.status === 200) {
          return res.json();
        }
        throw new Error("Something went wrong");
      })
      .then((data) => setComments(data))
      .catch((err) => {
        setStatus("ERROR");
        console.error(err);
      });
  }, []);

  const changeHandler = (
    e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    const id = e.target.id;
    const value = e.target.value;
    setNewComment((prevState) => ({ ...prevState, [id]: value }));
  };

  const submitHandler = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const newCommentWithId = { ...newComment, id: Math.random() };
    setComments((prevState) => [newCommentWithId, ...prevState]);
    fetch("https://jsonplaceholder.typicode.com/comments", {
      method: "POST",
      body: JSON.stringify(newCommentWithId),
    })
      .then((res) => {
        if (res.status === 201) {
          return res.json();
        }
        throw new Error("Something went wrong");
      })
      .then((data) => {})
      .catch((err) => {
        console.log(err);
        setComments((prevState) => {
          const newState = [...prevState];
          const index = newState.findIndex(
            (item) => item.id === newCommentWithId.id
          );
          newState.splice(index, 1);
          return newState;
        });
      });
  };

  
  return (
    <div>
      {status === "SUCCESS" ? (
        <>
          <h2>Book Details</h2>
          {book !== undefined && (
            <>
              <img className="cover" src={book.cover_image} height={100} />
              <ul>
                <li>Titolo: {book.title}</li>
                <li>Autore: {book.author}</li>
                <li>Anno: {book.publication_year}</li>
                <li>
                  Genere:
                  <ul>
                    {book.genre?.map((item) => (
                      <li>{item}</li>
                    ))}
                  </ul>
                </li>
                <li>Descrizione: {book.description}</li>
              </ul>
            </>
          )}
          <h3>Comments</h3>
          <form className="new_comment_form" onSubmit={submitHandler}>
            <div>New comment</div>
            <input id="name" placeholder="Name" onChange={changeHandler} />
            <input id="email" placeholder="Email" onChange={changeHandler} />
            <textarea
              id="body"
              placeholder="Your comment here"
              onChange={changeHandler}
            />
            <button className="submit_button" type="submit">
              Add
            </button>
          </form>
          {comments.map((item) => (
            <div key={item.id} className="comment">
              <div className="comment_name">{item.name}</div>
              <div className="comment_email">{item.email}</div>
              <div className="comment_body">{item.body}</div>
            </div>
          ))}
        </>
      ) : status === "ERROR" ? (
        <div>Ops... Something went wrong</div>
      ) : status === "LOADING" ? (
        <div>LOADING...</div>
      ) : null}
    </div>
  );
}

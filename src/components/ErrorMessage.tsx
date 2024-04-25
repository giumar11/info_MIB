import React from "react";

export function ErrorMessage({ isError, message }: { isError: boolean; message: string}) {
    return message ? <span className="error-message">{ message }</span> : null;
  }
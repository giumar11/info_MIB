import { object, string, boolean} from "yup";
import { CAMPO_OBBLIGATORIO, REQUIRED_FIELD, REQUIRED_FIELD_BOOLEAN } from "../labels";

export const validationSchema = object({
    username: string().required(CAMPO_OBBLIGATORIO), 
    email: string().email().required(CAMPO_OBBLIGATORIO), 
    password: string().required(CAMPO_OBBLIGATORIO),
    termsofuse: boolean().oneOf([false], "Must accept terms of use")
})


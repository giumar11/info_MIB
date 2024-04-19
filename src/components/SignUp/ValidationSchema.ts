import { array, boolean, date, mixed, number, object, ref, string } from "yup";
import { MATCH_PASSWORD, REQUIRED_FIELD, REQUIRED_FIELD_BOOLEAN } from "../labels";


export const validationSchema = object({
    name: string().required(REQUIRED_FIELD),
    
    lastname: string().required(REQUIRED_FIELD),
    
    genderassigned: string<'Female' | 'Male' | 'Other' >().required(REQUIRED_FIELD),

    genderselfidentified: string<'Female' | 'Male' | 'Nonbinary' >().required(REQUIRED_FIELD),

    citizenship: string().required(REQUIRED_FIELD),

    ethnicity: string().required(REQUIRED_FIELD),
    
    age: number().min(14, "Must be at least 14").required(REQUIRED_FIELD),
    
    username: string().required(REQUIRED_FIELD), 
    
    email: string().email().required(REQUIRED_FIELD),
    
    password: string().required(REQUIRED_FIELD).matches( /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})/, 
    "Must Contain 8 Characters, One Uppercase, One Lowercase, One Number and One Special Case Character"), 
    
    confirmpassword: string().required(REQUIRED_FIELD).oneOf([ref('password')], MATCH_PASSWORD),
    
    termsconditions: boolean().oneOf([false], "Must accept terms of use")
});


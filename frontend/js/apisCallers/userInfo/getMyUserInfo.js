import userInfoGet from "./userInfoGet.js";


export default async() => {
    
    const data = await userInfoGet('get_my_user_info', null);
    return data;
}
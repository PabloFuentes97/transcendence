import userInfoGet from "./userInfoGet.js";

export default async() => {
    
    const data = await userInfoGet('get_friends', null);
    return data;
}
import userInfoGet from "./userInfoGet.js";

export default async() => {
    
    const data = await userInfoGet('get_friend_requests', null);
    return data;
}
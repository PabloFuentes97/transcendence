import userInfoGet from "./userInfoGet.js";


export default async(userName) => {

    const data = await userInfoGet('get_user_info', 'username=' + userName);
    return data;
}
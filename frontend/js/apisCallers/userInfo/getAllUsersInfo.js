import userInfoGet from "./userInfoGet.js";

export default async(userName) => {

    const data = await userInfoGet('get_all_users_info', null);
    return data;
}
import userInfoGet from "./userInfoGet.js";


export default async(alias) => {

    const data = await userInfoGet('get_user_info_from_alias', 'alias=' + alias);
    return data;
}
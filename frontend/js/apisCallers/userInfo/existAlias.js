import userInfoGet from "./userInfoGet.js";

export default async(alias) => {

    const data = await userInfoGet('exist_alias', 'alias=' + alias);
    
    if ((await data) == null)
        return false
    if (data.answer == "alias exist")
        return true;
    return false;
}
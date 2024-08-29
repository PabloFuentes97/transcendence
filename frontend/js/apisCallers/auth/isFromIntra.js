import authServiceGet from "./authServiceGet.js";

export default async() => {

    const data = await authServiceGet('is_from_intra', "");
    if ((await data) == null)
        return false;
    return true;
}
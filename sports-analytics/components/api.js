// api.js
export const fetchDataFromApi = async (endpoint, params = {}) => {
  try {
    const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE_URL}/${endpoint}/`);
    Object.keys(params).forEach((key) =>
      url.searchParams.append(key, params[key])
    );

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching data:", error);
    return null;
  }
};

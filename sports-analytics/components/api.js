// api.js
export const fetchDataFromApi = async (endpoint, params = {}) => {
  try {
    const url = new URL(`http://127.0.0.1:8000/api/${endpoint}/`);
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

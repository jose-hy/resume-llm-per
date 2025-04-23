let isDevelopment = process.env.NODE_ENV === "development";
export const url = isDevelopment
  ? "http://localhost:8080"
  : "https://server.interviewmoves.org";

const request = (type: "POST" | "PUT" | "GET") => {
  return (
    endpoint: string,
    body?: { [index: string]: any },
    params?: { [index: string]: any },
  ) => {
    let obj = { ...params };

    if (type === "POST" || type === "PUT") {
      obj = {
        ...obj,
        method: type,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      };
    }

    return fetch(url + endpoint, {
      ...obj,
      credentials: "include",
    });
  };
};

export const get = (endpoint: string, params?: { [index: string]: any }) => {
  return request("GET")(endpoint, undefined, params);
};

export const post = request("POST");

export const put = request("PUT");

export const backendURL = (endpoint: string) =>
  `https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1${endpoint}`;

export const stateAbbreviations: Record<string, string> = {
  Alabama: "AL",
  Alaska: "AK",
  Arizona: "AZ",
  Arkansas: "AR",
  California: "CA",
  Colorado: "CO",
  Connecticut: "CT",
  Delaware: "DE",
  Florida: "FL",
  Georgia: "GA",
  Hawaii: "HI",
  Idaho: "ID",
  Illinois: "IL",
  Indiana: "IN",
  Iowa: "IA",
  Kansas: "KS",
  Kentucky: "KY",
  Louisiana: "LA",
  Maine: "ME",
  Maryland: "MD",
  Massachusetts: "MA",
  Michigan: "MI",
  Minnesota: "MN",
  Mississippi: "MS",
  Missouri: "MO",
  Montana: "MT",
  Nebraska: "NE",
  Nevada: "NV",
  "New Hampshire": "NH",
  "New Jersey": "NJ",
  "New Mexico": "NM",
  "New York": "NY",
  "North Carolina": "NC",
  "North Dakota": "ND",
  Ohio: "OH",
  Oklahoma: "OK",
  Oregon: "OR",
  Pennsylvania: "PA",
  "Rhode Island": "RI",
  "South Carolina": "SC",
  "South Dakota": "SD",
  Tennessee: "TN",
  Texas: "TX",
  Utah: "UT",
  Vermont: "VT",
  Virginia: "VA",
  Washington: "WA",
  "West Virginia": "WV",
  Wisconsin: "WI",
  Wyoming: "WY",
};

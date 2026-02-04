import type { JobListing } from "$lib/types";
import { backendURL, get } from "../../utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ request }) => {
  const res = await get("", {
    headers: {
      cookie: request.headers.get("cookie") || "",
    },
  });

  let defaultJobListings: JobListing[] = [];

  if (res.status === 200) {
    try {
      const res = await fetch(backendURL("/latest_jobs"));
      const data = await res.json();
      defaultJobListings = data;
    } catch (err) {
      console.log(err);
    }
  }

  return {
    isAuthed: res.status === 200,
    sessionID: crypto.randomUUID(),
    defaultJobListings,
  };
};
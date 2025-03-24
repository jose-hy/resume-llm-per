import type { JobListing } from "$lib/store.svelte";
import { get } from "../utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ request }) => {
  const res = await get("", {
    headers: {
      cookie: request.headers.get("cookie") || "",
    },
  });

  console.log(await res.text());

  let defaultJobListings: JobListing[] = [];

  if (res.status === 200) {
    try {
      const res = await fetch(
        "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/latest_jobs"
      );
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

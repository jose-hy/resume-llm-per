import type { JobListing } from "$lib/types";
import { backendURL } from "../utils";
import type { PageServerLoad } from "./$types";
import { redirect } from '@sveltejs/kit';
import { supabase } from '$lib/supabaseClient';

export const load: PageServerLoad = async ({ url, locals: { safeGetSession } }) => {
  const { session } = await safeGetSession()
  if (session) {
    redirect(303, "/profile");
  }

  const { data, error } = await supabase.from("jobs").select('*').not("posted_at", "is", "null").eq("is_active", true).limit(30).order('posted_at', {ascending: false});
  if (error) console.error('Connection failed:', error);

  let defaultJobListings: JobListing[] = [];

  try {
    defaultJobListings = data as JobListing[];
  } catch (err) {
    console.log(err);
  }

  return {
    sessionID: crypto.randomUUID(),
    defaultJobListings,
  };
};

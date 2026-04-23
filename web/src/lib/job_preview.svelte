<script lang="ts">
  import Spacer from "./spacer.svelte";
  import JobDialog from "$lib/job_dialog.svelte";
  import AppliedToDialog from "$lib/applied_to_dialog.svelte";
  import dayjs from "dayjs";
  import relativeTime from "dayjs/plugin/relativeTime";
  import { stateAbbreviations } from "../utils";
  import { createDialog } from "svelte-headlessui";
  import type { JobListing } from "./types";

  dayjs.extend(relativeTime);

  const {
    handleJobClicked,
    jobListing,
    jobListings,
    applied,
    userID,
    sessionID,
  }: {
    handleJobClicked: () => void;
    jobListing: JobListing;
    jobListings: JobListing[];
    applied: boolean;
    userID: string;
    sessionID: string;
  } = $props();

  const appliedToDialog = createDialog();

  const {
    id,
    job_id,
    title,
    company,
    location,
    description,
    apply_link,
    posted_at,
    embedding,
    similarity,
    is_remote,
    is_active,
    expires_at,
  } = jobListing;

  const [city, state] = location.split(",").map((s) => s.trim());
  const abbrState = stateAbbreviations[state];
  let descriptionPreview = description.slice(0, 200);
  const formattedTime = dayjs(posted_at).fromNow();
</script>

<div
  class="bg-white [border:1px_solid_#E6E6E6] rounded-8px
    max-[600px]:w-full w-[45vw] max-w-[650px] px-20px py-14px"
>
  <div class="flex justify-between gap-[20px]">
    <div>
      <p class="font-700 text-20px">{title}</p>
      <p class="14px font-500">
        {company}
      </p>
      <p class="14px">
        {city}, {abbrState} | {formattedTime}
      </p>
    </div>
    {#if jobListings}
      <p
        class="bg-[#ECE5AC] max-w-min whitespace-nowrap
        h-full px-[6px] py-4px rounded-4px text-14px"
      >
        {similarity ? `${(similarity * 100).toFixed(2)}% Match` : "New"}
      </p>
    {/if}
  </div>
  <Spacer axis="y" size="12" />
  <p class="text-[#383838]">
    {descriptionPreview + (descriptionPreview.at(-1) === "." ? "" : "...")}
  </p>
  <Spacer axis="y" size="24" />
  <div class="flex items-baseline gap-8px">
    <div>
      <a
        class="bg-black text-white rounded-4px px-12px py-4px h-full"
        href={apply_link}
        target="_blank"
        rel="noopener noreferrer"
        onclick={() => {
          handleJobClicked;
          appliedToDialog.open();
        }}
      > {#if applied}
          View Application
        {:else}
          Apply
        {/if}
      </a>
    </div>
    <JobDialog
      {description}
      {company}
      {title}
      {city}
      {abbrState}
      {apply_link}
      {formattedTime}
      {userID}
      {sessionID}
      {applied}
    />
    {#if !applied}
    <AppliedToDialog
      {userID}
      job_id={id}
      {title}
      {company}
      {location}
      {description}
      {apply_link}
      {is_remote}
      dialog={appliedToDialog}
    />
    {/if}
  </div>
</div>

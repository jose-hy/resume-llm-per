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
    file,
  }: {
    handleJobClicked: () => void;
    jobListing: JobListing;
    jobListings: JobListing[];
    file: File | null;
  } = $props();

  const appliedToDialog = createDialog();

  const generateScoreString = (score: number) => {
    let str = "";

    if (score <= 0.2) {
      str = "Minimal Match";
    } else if (score <= 0.4) {
      str = "Low Match";
    } else if (score <= 0.6) {
      str = "Moderate Match";
    } else if (score <= 0.8) {
      str = "Good Match";
    } else {
      str = "Strong Match";
    }

    return `${str} (${(score * 100).toFixed(0).toString()}%)`;
  };

  const {
    job_post_date,
    link,
    description,
    company,
    job_location,
    job_title,
    score,
    job_id,
    remote,
  } = jobListing;

  const [city, state] = job_location.split(",").map((s) => s.trim());
  const abbrState = { ...stateAbbreviations, "District of Columbia": "DC" }[
    state
  ];

  let descriptionPreview = description.slice(0, 200);

  const formattedTime = dayjs(job_post_date).fromNow();

  const scoreString = generateScoreString(score);
</script>

<div
  class="bg-white [border:1px_solid_#E6E6E6] rounded-8px
    max-[600px]:w-full w-[45vw] max-w-[650px] px-20px py-14px"
>
  <div class="flex justify-between gap-[20px]">
    <div>
      <p class="font-700 text-18px">{job_title}</p>
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
        {scoreString}
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
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        onclick={() => {
          handleJobClicked;
          appliedToDialog.open();
        }}
      >
        Apply
      </a>
    </div>
    <JobDialog
      {description}
      {company}
      {job_title}
      {city}
      {abbrState}
      {link}
      {formattedTime}
      {file}
    />
    <AppliedToDialog
      dialog={appliedToDialog}
      {remote}
      {link}
      {job_id}
      {job_location}
      {job_title}
    />
  </div>
</div>

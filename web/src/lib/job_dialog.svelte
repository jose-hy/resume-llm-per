<script lang="ts">
  import { createDialog } from "svelte-headlessui";
  import Transition from "svelte-transition";

  import Spacer from "./spacer.svelte";
  import ResumeAnalysis from "./resume_analysis.svelte";
  import CoverLetter from "./cover_letter.svelte";

  const {
    description,
    job_title,
    company,
    city,
    abbrState,
    link,
    formattedTime,
    file,
  } = $props();
  const dialog = createDialog();
  let page = $state("overview");
  let coverLetter = $state("");
  let disqualification = $state("");
  let improvement = $state("");

  const setCoverLetter = (s: string) => {
    coverLetter = s;
  };

  const setDisqualification = (s: string) => {
    disqualification = s;
  };

  const setImprovement = (s: string) => {
    improvement = s;
  };
</script>

<button
  type="button"
  class="[border:1px_solid_black] rounded-4px px-12px py-4px"
  onclick={dialog.open}>Learn more</button
>

<div class="relative z-10">
  <Transition show={$dialog.expanded}>
    <Transition
      enter="ease-out duration-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="ease-in duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <button
        class="fixed inset-0 bg-black bg-opacity-25"
        onclick={dialog.close}>close</button
      >
    </Transition>

    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 text-center">
        <Transition
          enterFrom="opacity-0 scale-95"
          enter="ease-out duration-300"
          enterTo="opacity-100 scale-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100 scale-100"
          leaveTo="opacity-0 scale-95"
        >
          <div
            class="w-full max-w-[800px] transform overflow-hidden rounded-12px
              bg-white p-6 text-left align-middle shadow-xl transition-all"
            use:dialog.modal
          >
            <div class="flex justify-between">
              <div>
                <p class="font-600 text-24px">{job_title}</p>
                <p>
                  {company} | {city}, {abbrState} | {formattedTime}
                </p>
              </div>
              <a
                class="bg-black text-white rounded-4px px-12px py-4px h-full"
                href={link}
                target="_blank"
                rel="noopener noreferrer"
              >
                Apply
              </a>
            </div>
            <Spacer axis="y" size="24" />

            <div
              class="flex gap-16px bg-[#F2F2F2] px-12px py-8px rounded-7px w-min"
            >
              <button
                onclick={() => (page = "overview")}
                class={page === "overview"
                  ? "bg-white px-8px py-4px rounded-7px"
                  : ""}>Overview</button
              >
              <button
                onclick={() => (page = "resume-analysis")}
                class={`${
                  page === "resume-analysis"
                    ? "bg-white px-8px py-4px rounded-7px"
                    : ""
                } whitespace-nowrap`}
              >
                Resume analysis
              </button>
              <button
                onclick={() => (page = "cover-letter")}
                class={`${
                  page === "cover-letter"
                    ? "bg-white px-8px py-4px rounded-7px"
                    : ""
                } whitespace-nowrap`}>Generate cover letter</button
              >
            </div>
            <Spacer size={24} axis="y" />
            {#if page === "overview"}
              <p class="whitespace-pre-line">{description}</p>
            {:else if page === "resume-analysis"}
              <ResumeAnalysis
                {setImprovement}
                {setDisqualification}
                {disqualification}
                {improvement}
                {description}
                {file}
              />
            {:else}
              <CoverLetter
                {setCoverLetter}
                {coverLetter}
                {description}
                {file}
              />
            {/if}
            <Spacer size={24} axis="y" />
            <button
              type="button"
              class="bg-black text-white rounded-4px px-12px py-4px h-full"
              onclick={dialog.close}
            >
              Close
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</div>

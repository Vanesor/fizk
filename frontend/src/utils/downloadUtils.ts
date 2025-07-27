/**
 * Utilities for downloading files and creating downloadable content
 */

/**
 * Download the seed generator tool as a zip file
 */
export const downloadSeedGenerator = () => {
  // URL to the seed generator zip file stored in public directory
  const seedGenUrl = "/assets/seedgen.zip";

  // Create an anchor element for downloading
  const link = document.createElement("a");
  link.href = seedGenUrl;
  link.download = "fizk-seedgen.zip";
  link.target = "_blank";

  // Append to body, trigger click, and remove
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  return true;
};

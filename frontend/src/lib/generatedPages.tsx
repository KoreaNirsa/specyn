import type { ComponentType } from "react";

const generatedPageModules = import.meta.glob("../generated/**/GeneratedProjectPage.tsx");

function projectIdFromModulePath(modulePath: string): string | null {
  const segments = modulePath.split("/");
  const generatedIndex = segments.findIndex((segment) => segment === "generated");
  if (generatedIndex < 0 || generatedIndex + 1 >= segments.length) {
    return null;
  }
  return segments[generatedIndex + 1] ?? null;
}

export function listGeneratedProjectIds(): string[] {
  return Object.keys(generatedPageModules)
    .map(projectIdFromModulePath)
    .filter((value): value is string => Boolean(value))
    .sort();
}

export async function loadGeneratedProjectComponent(
  projectId: string,
): Promise<ComponentType | null> {
  const matchedEntry = Object.entries(generatedPageModules).find(([modulePath]) => {
    return projectIdFromModulePath(modulePath) === projectId;
  });

  if (!matchedEntry) {
    return null;
  }

  const [, loader] = matchedEntry;
  const module = await loader();
  const component = (module as { default?: ComponentType }).default;
  return component ?? null;
}

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { APPLICATION_SURFACES, type ApplicationSurface } from "./surface-config";

export interface AppShellRealmContext {
  id?: string;
  name?: string;
  realmType?: string;
}

export interface AppShellUserContext {
  id?: string;
  label?: string;
  permissions?: string[];
}

interface AppShellContextValue {
  surface: ApplicationSurface;
  featureFlags: string[];
  realmContext: AppShellRealmContext | null;
  userContext: AppShellUserContext | null;
}

const AppShellContext = createContext<AppShellContextValue>({
  surface: "public",
  featureFlags: [],
  realmContext: null,
  userContext: null,
});

export function useAppShell(): AppShellContextValue {
  return useContext(AppShellContext);
}

interface AppShellProps {
  surface: ApplicationSurface;
  navRail?: ReactNode;
  contextBar?: ReactNode;
  mobileNav?: ReactNode;
  statusStrip?: ReactNode;
  rightDrawer?: ReactNode;
  featureFlags?: string[];
  realmContext?: AppShellRealmContext;
  userContext?: AppShellUserContext;
  children: ReactNode;
}

export default function AppShell({
  surface,
  navRail,
  contextBar,
  mobileNav,
  statusStrip,
  rightDrawer,
  featureFlags = [],
  realmContext,
  userContext,
  children,
}: AppShellProps) {
  const protocol = APPLICATION_SURFACES[surface];
  const contextValue = useMemo(
    () => ({
      surface,
      featureFlags,
      realmContext: realmContext || null,
      userContext: userContext || null,
    }),
    [featureFlags, realmContext, surface, userContext],
  );
  return (
    <AppShellContext.Provider value={contextValue}>
      <div
        className="v106-app-shell flex min-h-screen"
        data-application-surface={surface}
        data-feature-flags={featureFlags.join(",")}
        data-realm-context={realmContext?.id || ""}
        data-user-context={userContext?.id || ""}
        aria-label={`${protocol.label}统一壳层`}
      >
        {navRail}
        <div className="flex min-w-0 flex-1 flex-col">
          {contextBar}
          {mobileNav}
          <main className="min-w-0 flex-1 px-4 py-4 lg:px-6 lg:py-5">{children}</main>
          {statusStrip && (
            <footer className="border-t border-[color:var(--v106-border)] bg-white px-4 py-3 lg:px-6">
              {statusStrip}
            </footer>
          )}
        </div>
        {rightDrawer}
      </div>
    </AppShellContext.Provider>
  );
}

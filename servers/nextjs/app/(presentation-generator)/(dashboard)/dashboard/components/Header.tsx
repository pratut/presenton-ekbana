"use client";

import Wrapper from "@/components/Wrapper";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { trackEvent, MixpanelEvent } from "@/utils/mixpanel";
import { useAuth } from "@/components/auth/AuthContext";
import { useRouter } from "next/navigation";
import { useDispatch } from "react-redux";
import { defaultLLMConfig, setLLMConfig } from "@/store/slices/userConfig";
const Header = () => {
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useDispatch();
  const { session, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    dispatch(setLLMConfig(defaultLLMConfig));
    router.replace("/login");
  };
  return (
    <div className="w-full  sticky top-0 z-50 py-7 ">
      <Wrapper className="px-5 sm:px-10 lg:px-20">
        <div className="flex items-center justify-between py-1">
          <div className="flex items-center gap-3">
            {/* {(pathname !== "/upload" && pathname !== "/dashboard") && <BackBtn />} */}
            <Link href="/dashboard" onClick={() => trackEvent(MixpanelEvent.Navigation, { from: pathname, to: "/dashboard" })}>
              <img
                src="/logo-with-bg.png"
                alt="Presentation logo"
                className="h-[40px] w-[40px]"
              />
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-600 font-syne">{session?.email}</span>
            <button
              onClick={handleLogout}
              className="text-xs font-medium px-3 py-2 rounded-md border border-slate-200 text-slate-700 hover:bg-slate-50"
            >
              Logout
            </button>
          </div>

        </div>
      </Wrapper>
    </div>
  );
};

export default Header;

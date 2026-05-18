import { Badge } from "@/components/ui/badge";
import { getDefectLabel } from "@/lib/constants";
import type { DefectType, Verdict } from "@/lib/types";

interface DefectBadgeProps {
  verdict: Verdict;
  defectType: DefectType;
}

export function DefectBadge({ verdict, defectType }: DefectBadgeProps) {
  if (verdict === "ok") {
    return (
      <Badge variant="secondary" className="font-normal">
        OK
      </Badge>
    );
  }

  return (
    <Badge variant="destructive" className="font-normal">
      {getDefectLabel(defectType)}
    </Badge>
  );
}

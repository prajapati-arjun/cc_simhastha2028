import ServiceCard from "./ServiceCard";
import type { EssentialService } from "./accommodationApi";

export function ServiceList({ items }: { items: EssentialService[] }) {
  return (
    <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
      {items.map((item) => (
        <ServiceCard key={item.id} item={item} />
      ))}
    </div>
  );
}

export default ServiceList;

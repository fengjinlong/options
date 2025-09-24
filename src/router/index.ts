import { createRouter, createWebHistory } from "vue-router";
import StrategyList from "../components/StrategyList.vue";
import OptionCalendarChart from "../components/OptionCalendarChart.vue";
import SolVolatility from "../views/SolVolatility.vue";
import CmcVolatility from "../views/CmcVolatility.vue";
import VolatilityChart from "../components/VolatilityChart.vue";
import DvolChart from "../components/DvolChart.vue";
import OptionsCalculator from "../views/OptionsCalculator.vue";
import Sjfx from "../views/Sjfx.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: StrategyList,
    },
    {
      path: "/calendar-call",
      name: "calendar-call",
      component: OptionCalendarChart,
    },
    {
      path: "/sol-volatility",
      name: "sol-volatility",
      component: SolVolatility,
    },
    {
      path: "/cmc-volatility",
      name: "cmc-volatility",
      component: CmcVolatility,
    },
    {
      path: "/derbit-volatility",
      name: "historical-volatility",
      component: VolatilityChart,
    },
    {
      path: "/dvol-chart",
      name: "dvol-chart",
      component: DvolChart,
    },
    {
      path: "/options-calculator",
      name: "options-calculator",
      component: OptionsCalculator,
    },
    {
      path: "/sjfx",
      name: "sjfx",
      component: Sjfx,
    },
  ],
});

export default router;

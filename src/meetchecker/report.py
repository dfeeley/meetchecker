import datetime
import itertools
from operator import attrgetter
import textwrap


class LaneResultsHtmlAdapter:
    def __init__(self, lane_results):
        self.lane_results = lane_results

    def generate_table(self):
        out = []
        out.append('<table class="meetchecker">')
        out.append("<tbody>")
        for event_no, event_records_iter in itertools.groupby(
            self.lane_results, key=attrgetter("event_no")
        ):
            event_records = list(event_records_iter)
            out.append('<tr class="event"><td colspan="5">')
            out.append(
                f"Event {event_records[0].event_no}: {event_records[0].event_name}"
            )
            out.append("</td></tr>")

            for fin_heat, heat_records_iter in itertools.groupby(
                event_records, key=attrgetter("fin_heat")
            ):
                heat_records = list(heat_records_iter)
                out.append('<tr class="heat"><td colspan="5">')
                out.append(f"Heat: {heat_records[0].fin_heat}")
                out.append("</td></tr>")

                for lane_result in heat_records:
                    out.append('<tr class="lane">')
                    out.append(f"<td>Lane {lane_result.fin_lane}</td>")
                    out.append(f"<td>{lane_result.athlete_name}</td>")
                    out.append(f"<td>{lane_result.team_abbr}</td>")
                    out.append(f"<td>{lane_result.fin_time:.2f}</td>")
                    out.append("</td></tr>")

                    out.append('<tr class="reasons"><td colspan="5"><ul>')
                    for name_reason in lane_result.name_reasons:
                        out.append(
                            f'<li class="reason">{name_reason.name}: {name_reason.reason}</li>'
                        )
                    out.append("</ul></td></tr>")
        out.append("</tbody></table>")
        return "".join(out)


def inline_css():
    return textwrap.dedent(
        """<style>
          tr.event {
            font-weight: bold;
            font-size: 1.2rem;
            background: #ccc;
          }

          tr.heat td {
            border-bottom: 1px solid black;
          }

          tr.heat td:first-of-type {
            padding-left: 15px;
          }

          tr.lane td:first-of-type {
           padding-left: 30px;
          }

          tr.reasons td:first-of-type {
            padding-left: 45px;
          }
          .breadcrumb-title {
            font-weight: 700;
          }
}    </style>"""
    )


def report_header(meetfile):
    timestamp = str(datetime.datetime.now())
    return f"""
        <h1>Meet Manager data checks report</h1>
        <p>
            <span class="breadcrumb-title">File:</span>
            <span class="breadcrumb-value">{meetfile}</span>
        </p>
        <p>
            <span class="breadcrumb-title">Generated:</span>
            <span class="breadcrumb-value">{timestamp}</span>
        </p>"""


def report_javascript(idle_duration=30):
    return (
        """
        <script>
        function getQueryVariable(variable)
        {
               var query = window.location.search.substring(1);
               var vars = query.split("&");
               for (var i=0;i<vars.length;i++) {
                       var pair = vars[i].split("=");
                       if(pair[0] == variable){return pair[1];}
               }
               return(false);
        }


        (function() {

            let refresh = getQueryVariable('refresh')
            if (refresh & refresh != '0') {
                console.log('Refresh is enabled');
        """
        f"const idleDurationSecs = {idle_duration};"
        """
                const redirectUrl = location.href;
                let idleTimeout; // variable to hold the timeout, do not modify

                const resetIdleTimeout = function() {

                    // Clears the existing timeout
                    if(idleTimeout) clearTimeout(idleTimeout);

                    // Set a new idle timeout to load the redirectUrl after idleDurationSecs
                    idleTimeout = setTimeout(() => location.href = redirectUrl, idleDurationSecs * 1000);
                };

                // Init on page load
                resetIdleTimeout();

                // Reset the idle timeout on any of the events listed below
                ['click', 'touchstart', 'mousemove'].forEach(evt =>
                    document.addEventListener(evt, resetIdleTimeout, false)
                );
            } else {
                console.log('Refresh is not enabled');
            }

        })();
        </script>
    """
    )


def create_html_report(lane_results, meetfile, output):
    out = []
    out.append("<html>")
    out.append("<head>")
    out.append(inline_css())
    out.append("</head>")
    out.append("<body>")
    out.append(report_header(meetfile))
    adapter = LaneResultsHtmlAdapter(lane_results)
    out.append(adapter.generate_table())
    out.append(report_javascript())
    out.append("</body>")
    out.append("</html>")
    with open(output, "w") as f:
        f.write("".join(out))

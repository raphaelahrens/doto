import cProfile
import pstats
import io


def profile_this():
    import doto
    doto.main()


pr = cProfile.Profile()
pr.enable()

profile_this()

pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
print("LOL")
